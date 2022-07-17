from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from app.config import hs_data

KeyboardMarkup = ReplyKeyboardMarkup | InlineKeyboardMarkup | ReplyKeyboardRemove | None
Btns = list[tuple[str | InlineKeyboardButton, ...] | str]

command_cd = CallbackData('cmd', 'scope', 'action')
cardparam_cd = CallbackData('cpd', 'param', 'action')
cardlist_cd = CallbackData('cld', 'id', 'action')


class KeyboardBuilder:

    def __init__(self, data: dict):
        self.data = data
        self.keyboard: KeyboardMarkup = None

    def fill(self, buttons: Btns) -> None:
        """
        Fill self.keyboard with buttons

        :raise AttributeError: if self.keyboard hasn't been initialized yet
        :raise ValueError: if buttons have an unsupported format
        """
        if not self.keyboard:
            raise AttributeError('Attempt to fill the keyboard before initialization')

        self.keyboard.resize_keyboard = True
        for row in buttons:
            match row:
                case str() | InlineKeyboardButton() as btn:
                    self.keyboard.add(btn)
                case tuple() as btns:
                    self.keyboard.add(*btns)
                case _:
                    raise ValueError(f'Invalid keyboard row: {row}')

    @staticmethod
    def group_buttons(buttons: list[str | InlineKeyboardButton],
                      cols: int = 2) -> list[tuple[str | InlineKeyboardButton, ...]]:
        """ Reshape array of buttons for __fill() method """
        btn_array = []
        row = []

        for idx, btn in enumerate(buttons, start=1):
            row.append(btn)
            if idx % cols == 0:
                btn_array.append(tuple(row))
                row.clear()

        match len(row):
            case 0:
                pass
            case 1:
                btn_array.extend(row)
            case _:
                btn_array.append(tuple(row))
        return btn_array


class CommonKeyboardBuilder(KeyboardBuilder):

    def default(self) -> KeyboardMarkup:
        """ Return default Reply KeyboardMarkup to show in main menu """
        buttons = [
            ('Cards', 'Decks'),
            'Decode Deckstring',
        ]
        self.keyboard = ReplyKeyboardMarkup()
        self.fill(buttons)
        return self.keyboard


class CardKeyboardBuilder(KeyboardBuilder):

    def request_info(self) -> InlineKeyboardMarkup:
        """ Build a keyboard for RequestInfoMessage """
        buttons = [
            (
                InlineKeyboardButton('Name', callback_data=cardparam_cd.new(param='name', action='add')),
                InlineKeyboardButton('Type', callback_data=cardparam_cd.new(param='ctype', action='add')),
                InlineKeyboardButton('Class', callback_data=cardparam_cd.new(param='classes', action='add')),
            ),
            (
                InlineKeyboardButton('Set', callback_data=cardparam_cd.new(param='cset', action='add')),
                InlineKeyboardButton('Rarity', callback_data=cardparam_cd.new(param='rarity', action='add')),
                InlineKeyboardButton('Cost', callback_data=cardparam_cd.new(param='cost', action='add')),
            ),
        ]

        match self.data.get('ctype'):
            case 'M':
                buttons.append((
                    InlineKeyboardButton('Attack', callback_data=cardparam_cd.new(param='attack', action='add')),
                    InlineKeyboardButton('Health', callback_data=cardparam_cd.new(param='health', action='add')),
                ))
            case 'W':
                buttons.append((
                    InlineKeyboardButton('Attack', callback_data=cardparam_cd.new(param='attack', action='add')),
                    InlineKeyboardButton(
                        'Durability',
                        callback_data=cardparam_cd.new(param='durability', action='add'),
                    ),
                ))
            case 'H':
                buttons.append(
                    InlineKeyboardButton('Armor', callback_data=cardparam_cd.new(param='armor', action='add')),
                )

        buttons.append((
            InlineKeyboardButton('Language', callback_data=cardparam_cd.new(param='language', action='add')),
            InlineKeyboardButton('Collectible', callback_data=cardparam_cd.new(param='coll', action='add')),
        ))

        buttons.append((
            InlineKeyboardButton('REQUEST', callback_data=command_cd.new(scope='card_request', action='request')),
            InlineKeyboardButton('CLEAR', callback_data=command_cd.new(scope='card_request', action='clear')),
            InlineKeyboardButton('CLOSE', callback_data=command_cd.new(scope='card_request', action='close')),
        ))
        self.keyboard = InlineKeyboardMarkup()
        self.fill(buttons)

        return self.keyboard

    def wait_param(self, param: str) -> InlineKeyboardMarkup:
        """
        Return a keyboard for receiving parameters

        :raise ValueError: if param is unsupported
        """
        lower_row = [InlineKeyboardButton('CANCEL', callback_data=cardparam_cd.new(param=param, action='cancel'))]

        if self.data.get(param):
            lower_row.append(
                InlineKeyboardButton('CLEAR', callback_data=cardparam_cd.new(param=param, action='clear'))
            )

        match param:
            case 'name' | 'cost' | 'attack' | 'health' | 'durability' | 'armor':
                buttons = []
            case 'ctype':
                type_buttons = [InlineKeyboardButton(t.en, callback_data=cardparam_cd.new(param=t.sign, action='add'))
                                for t in hs_data.types]
                buttons = self.group_buttons(type_buttons)
            case 'classes':
                class_buttons = [InlineKeyboardButton(c.en, callback_data=cardparam_cd.new(param=c.en, action='add'))
                                 for c in hs_data.classes]
                buttons = self.group_buttons(class_buttons)
            case 'cset':
                set_buttons = [InlineKeyboardButton(s.en, callback_data=cardparam_cd.new(param=s.en, action='add'))
                               for s in hs_data.sets]
                buttons = self.group_buttons(set_buttons)
            case 'rarity':
                rarity_buttons = [InlineKeyboardButton(r.en, callback_data=cardparam_cd.new(param=r.sign, action='add'))
                                  for r in hs_data.rarities]
                buttons = self.group_buttons(rarity_buttons)
            case _:
                raise ValueError(f'Unknown card parameter: {param}')

        buttons.append(tuple(lower_row))

        self.keyboard = InlineKeyboardMarkup()
        self.fill(buttons)
        return self.keyboard

    def result_list(self):
        """ Return a keyboard to control CardList message """
        page = self.data['cardlist']['page']
        all_cards = self.data['cardlist']['cards']
        total_pages = len(all_cards)
        page_cards = all_cards[page - 1] if all_cards else []

        card_buttons = [
            InlineKeyboardButton(f'{i}. {card["name"]}',
                                 callback_data=cardlist_cd.new(id=card['dbf_id'], action='get'))
            for i, card in enumerate(page_cards, start=1)
        ]
        card_buttons = self.group_buttons(card_buttons, cols=3)

        page_buttons = []
        if total_pages > 1:
            page_buttons = [
                InlineKeyboardButton('◄', callback_data=command_cd.new(scope='card_pages', action='left')),
                InlineKeyboardButton(
                    f'| Page {page} of {total_pages} |',
                    callback_data=command_cd.new(scope='card_pages', action='pages'),
                ),
                InlineKeyboardButton('►', callback_data=command_cd.new(scope='card_pages', action='right')),
            ]

        control_buttons = [
            InlineKeyboardButton('CLOSE', callback_data=command_cd.new(scope='card_pages', action='close')),
        ]

        card_buttons.append(tuple(page_buttons))
        card_buttons.append(tuple(control_buttons))

        self.keyboard = InlineKeyboardMarkup()
        self.fill(card_buttons)
        return self.keyboard

    def result_detail(self):
        """ Return a keyboard to control CardDetail message """
        buttons = [
            InlineKeyboardButton('Find decks!', callback_data=command_cd.new(scope='card_detail', action='decks')),
            (
                InlineKeyboardButton('BACK', callback_data=command_cd.new(scope='card_detail', action='back')),
                InlineKeyboardButton('CLOSE', callback_data=command_cd.new(scope='card_pages', action='close')),
            ),
        ]
        self.keyboard = InlineKeyboardMarkup()
        self.fill(buttons)
        return self.keyboard


class DeckKeyboardBuilder(KeyboardBuilder):
    pass


class Keyboard:

    def __init__(self, data: dict):
        self.__data = data

    @property
    def common(self):
        return CommonKeyboardBuilder(self.__data)

    @property
    def cards(self):
        return CardKeyboardBuilder(self.__data)

    @property
    def decks(self):
        return DeckKeyboardBuilder(self.__data)
