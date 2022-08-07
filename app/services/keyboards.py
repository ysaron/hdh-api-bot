from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from app.config import hs_data

KeyboardMarkup = ReplyKeyboardMarkup | InlineKeyboardMarkup | ReplyKeyboardRemove | None
Btns = list[tuple[str | InlineKeyboardButton, ...] | str]

command_cd = CallbackData('cmd', 'scope', 'action', 'on_close')
cardparam_cd = CallbackData('cpd', 'param', 'action')
cardlist_cd = CallbackData('cld', 'id', 'action')
deckparam_cd = CallbackData('dpd', 'param', 'action')
decklist_cd = CallbackData('dld', 'id', 'action')


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
        """ Build a keyboard for CardRequestInfoMessage """
        state_on_close = self.data.get('on_close', '')
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
            case 'L':
                buttons.append(
                    InlineKeyboardButton('Health', callback_data=cardparam_cd.new(param='health', action='add')),
                )

        buttons.append((
            InlineKeyboardButton('Language', callback_data=cardparam_cd.new(param='language', action='add')),
            InlineKeyboardButton('Collectible', callback_data=cardparam_cd.new(param='coll', action='add')),
        ))

        buttons.append((
            InlineKeyboardButton('REQUEST ✅', callback_data=command_cd.new(scope='card_request',
                                                                           action='request',
                                                                           on_close='')),
            InlineKeyboardButton('CLEAR 🗑', callback_data=command_cd.new(
                scope='card_request',
                action='clear',
                on_close='',
            )),
            InlineKeyboardButton('CLOSE ❌', callback_data=command_cd.new(
                scope='card_request',
                action='close',
                on_close=state_on_close,
            )),
        ))
        self.keyboard = InlineKeyboardMarkup()
        self.fill(buttons)

        return self.keyboard

    def wait_param(self, param: str) -> InlineKeyboardMarkup:
        """
        Return a keyboard for receiving card parameters

        :raise ValueError: if param is unsupported
        """
        lower_row = [InlineKeyboardButton('CANCEL ❌', callback_data=cardparam_cd.new(param=param, action='cancel'))]

        if self.data.get(param):
            lower_row.append(
                InlineKeyboardButton('CLEAR 🗑', callback_data=cardparam_cd.new(param=param, action='clear'))
            )

        match param:
            case 'name' | 'cost' | 'attack' | 'health' | 'durability' | 'armor':
                buttons = []
            case 'ctype':
                type_btns = [InlineKeyboardButton(t.en, callback_data=cardparam_cd.new(param=t.sign, action='submit'))
                             for t in hs_data.types]
                buttons = self.group_buttons(type_btns)
            case 'classes':
                class_btns = [InlineKeyboardButton(c.en, callback_data=cardparam_cd.new(param=c.en, action='submit'))
                              for c in hs_data.classes]
                buttons = self.group_buttons(class_btns)
            case 'cset':
                set_btns = [InlineKeyboardButton(s.en, callback_data=cardparam_cd.new(param=s.en, action='submit'))
                            for s in hs_data.sets]
                buttons = self.group_buttons(set_btns)
            case 'rarity':
                rarity_btns = [InlineKeyboardButton(r.en, callback_data=cardparam_cd.new(param=r.sign, action='submit'))
                               for r in hs_data.rarities]
                buttons = self.group_buttons(rarity_btns)
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
                                 callback_data=cardlist_cd.new(id=card['dbf_id'], action='getcard'))
            for i, card in enumerate(page_cards, start=1)
        ]
        card_buttons = self.group_buttons(card_buttons, cols=3)

        page_buttons = []
        if total_pages > 1:
            page_buttons = [
                InlineKeyboardButton('⬅️', callback_data=command_cd.new(
                    scope='card_pages',
                    action='left',
                    on_close='',
                )),
                InlineKeyboardButton(
                    f'| Page {page} of {total_pages} |',
                    callback_data=command_cd.new(scope='card_pages', action='pages', on_close=''),
                ),
                InlineKeyboardButton('➡️', callback_data=command_cd.new(
                    scope='card_pages',
                    action='right',
                    on_close='',
                )),
            ]

        control_buttons = [
            InlineKeyboardButton('CLOSE ❌', callback_data=command_cd.new(scope='card_pages',
                                                                         action='close',
                                                                         on_close='')),
        ]

        card_buttons.append(tuple(page_buttons))
        card_buttons.append(tuple(control_buttons))

        self.keyboard = InlineKeyboardMarkup()
        self.fill(card_buttons)
        return self.keyboard

    def result_detail(self):
        """ Return a keyboard to control CardDetail message """
        card = self.data['card_detail']
        if self.data.get('on_close'):
            first_btn = InlineKeyboardButton('✅ Add this card to deck request',
                                             callback_data=cardlist_cd.new(id=card['dbf_id'], action='addcard'))
        else:
            first_btn = InlineKeyboardButton('↖️ Find decks!',
                                             callback_data=cardlist_cd.new(id=card['dbf_id'], action='getdecks'))
        buttons = [
            first_btn,
            (
                InlineKeyboardButton('BACK ↩️', callback_data=command_cd.new(
                    scope='card_detail',
                    action='back',
                    on_close='',
                )),
                InlineKeyboardButton('CLOSE ❌', callback_data=command_cd.new(
                    scope='card_pages',
                    action='close',
                    on_close='',
                )),
            ),
        ]
        self.keyboard = InlineKeyboardMarkup()
        self.fill(buttons)
        return self.keyboard


class DeckKeyboardBuilder(KeyboardBuilder):

    def request_info(self) -> InlineKeyboardMarkup:
        """ Build a keyboard for DeckRequestInfoMessage """
        buttons = [
            (
                InlineKeyboardButton('Format', callback_data=deckparam_cd.new(param='dformat', action='add')),
                InlineKeyboardButton('Class', callback_data=deckparam_cd.new(param='dclass', action='add')),
            ),
            (
                InlineKeyboardButton(
                    'Created after',
                    callback_data=deckparam_cd.new(param='deck_created_after', action='add'),
                ),
                InlineKeyboardButton('Cards', callback_data=deckparam_cd.new(param='deck_cards', action='add')),
            ),
            InlineKeyboardButton('Language', callback_data=deckparam_cd.new(param='language', action='add')),
            (
                InlineKeyboardButton('REQUEST ✅', callback_data=command_cd.new(
                    scope='deck_request',
                    action='request',
                    on_close='',
                )),
                InlineKeyboardButton('CLEAR 🗑', callback_data=command_cd.new(
                    scope='deck_request',
                    action='clear',
                    on_close='',
                )),
                InlineKeyboardButton('CLOSE ❌', callback_data=command_cd.new(
                    scope='deck_request',
                    action='close',
                    on_close='',
                )),
            )
        ]

        self.keyboard = InlineKeyboardMarkup()
        self.fill(buttons)

        return self.keyboard

    def wait_param(self, param: str) -> InlineKeyboardMarkup:
        """
        Return a keyboard for receiving deck parameters

        :raise ValueError: if param is unsupported
        """
        lower_row = [InlineKeyboardButton('CANCEL ❌', callback_data=deckparam_cd.new(param=param, action='cancel'))]

        if self.data.get(param):
            lower_row.append(
                InlineKeyboardButton('CLEAR 🗑', callback_data=deckparam_cd.new(param=param, action='clear'))
            )

        match param:
            case 'deck_created_after':
                buttons = []
            case 'dformat':
                fmt_btns = [InlineKeyboardButton(f.en, callback_data=deckparam_cd.new(param=f.en, action='submit'))
                            for f in hs_data.formats]
                buttons = self.group_buttons(fmt_btns)
            case 'dclass':
                class_btns = [InlineKeyboardButton(c.en, callback_data=deckparam_cd.new(param=c.en, action='submit'))
                              for c in hs_data.classes if c.en.lower() != 'neutral']
                buttons = self.group_buttons(class_btns)
            case _:
                raise ValueError(f'Unknown deck parameter: {param}')
        buttons.append(tuple(lower_row))

        self.keyboard = InlineKeyboardMarkup()
        self.fill(buttons)
        return self.keyboard

    def result_list(self):
        """ Return a keyboard to control DeckList message """
        state_on_close = self.data['on_close']
        page = self.data['deck_list']['page']
        all_decks = self.data['deck_list']['decks']
        total_pages = len(all_decks)
        page_decks = all_decks[page - 1] if all_decks else []

        deck_buttons = [
            InlineKeyboardButton(f'{i}. id{deck["id"]} {deck["deck_format"]} {deck["deck_class"]}',
                                 callback_data=decklist_cd.new(id=deck['id'], action='get'))
            for i, deck in enumerate(page_decks, start=1)
        ]
        deck_buttons = self.group_buttons(deck_buttons, cols=3)

        page_buttons = []
        if total_pages > 1:
            page_buttons = [
                InlineKeyboardButton('⬅️', callback_data=command_cd.new(
                    scope='deck_pages',
                    action='left',
                    on_close='',
                )),
                InlineKeyboardButton(f'| Page {page} of {total_pages} |', callback_data=command_cd.new(
                    scope='deck_pages',
                    action='pages',
                    on_close='',
                )),
                InlineKeyboardButton('➡️', callback_data=command_cd.new(
                    scope='deck_pages',
                    action='right',
                    on_close='',
                )),
            ]

        control_buttons = [
            InlineKeyboardButton('CLOSE ❌', callback_data=command_cd.new(scope='deck_pages',
                                                                         action='close',
                                                                         on_close=state_on_close)),
        ]

        deck_buttons.append(tuple(page_buttons))
        deck_buttons.append(tuple(control_buttons))

        self.keyboard = InlineKeyboardMarkup()
        self.fill(deck_buttons)
        return self.keyboard

    def result_detail(self):
        """ Return a keyboard to control DeckDetail message """
        buttons = [
            (
                InlineKeyboardButton('BACK ↩️', callback_data=command_cd.new(scope='deck_detail',
                                                                             action='back',
                                                                             on_close='')),
                InlineKeyboardButton('CLOSE ❌', callback_data=command_cd.new(scope='deck_pages',
                                                                             action='close',
                                                                             on_close='')),
            ),
        ]
        self.keyboard = InlineKeyboardMarkup()
        self.fill(buttons)
        return self.keyboard


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
