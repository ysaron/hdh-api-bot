from aiogram.utils import markdown as md

from app.config import hs_data, CARD_RENDER_BASE_URL


class TextBuilder:
    """ Build text consisting of formatable rows """

    def __init__(self):
        self.rows: list[str] = []

    def format(self):
        """ Fill self.rows """
        pass

    def as_text(self) -> str:
        """ Return text ready to send as Telegram message """
        if not self.rows:
            return '--empty--'
        return '\n'.join(self.rows)


class CardRequestInfo(TextBuilder):
    """ Encapsulates text of RequestInfoMessage """

    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self.header = '<b>►►► <u>Build request</u> ◄◄◄</b>'
        self.language = 'Language: <b>English</b>'
        self.collectible = 'Collectible: <b>Yes</b>'
        self.name = 'Name: <b><u>{}</u></b>'
        self.ctype = 'Type: <b>{}</b>'
        self.classes = 'Classes: <b>{}</b>'
        self.cset = 'Set: <b>{}</b>'
        self.rarity = 'Rarity: <b>{}</b>'
        self.cost = 'Cost: <b>{}</b>'
        self.attack = 'Attack: <b>{}</b>'
        self.health = 'Health: <b>{}</b>'
        self.durability = 'Durability: <b>{}</b>'
        self.armor = 'Armor: <b>{}</b>'

    def format(self):
        """ Format and collect rows """

        self.rows.append(self.header)
        self.rows.append(self.language)
        self.rows.append(self.collectible)
        if self.data.get('name'):
            self.rows.append(self.name.format(self.data['name']))
        if self.data.get('ctype'):
            verbose_type = hs_data.gettype(self.data['ctype']).en
            self.rows.append(self.ctype.format(verbose_type))
        if self.data.get('classes'):
            verbose_class = ','.join(self.data['classes'])
            self.rows.append(self.classes.format(verbose_class))
        if self.data.get('cset'):
            self.rows.append(self.cset.format(self.data['cset']))
        if self.data.get('rarity'):
            verbose_rarity = hs_data.getrarity(sign=self.data['rarity']).en
            self.rows.append(self.rarity.format(verbose_rarity))
        if self.data.get('cost'):
            self.rows.append(self.cost.format(self.data['cost']))
        if self.data.get('attack'):
            self.rows.append(self.attack.format(self.data['attack']))
        if self.data.get('health'):
            self.rows.append(self.health.format(self.data['health']))
        if self.data.get('durability'):
            self.rows.append(self.durability.format(self.data['durability']))
        if self.data.get('armor'):
            self.rows.append(self.armor.format(self.data['armor']))

    def as_text(self) -> str:
        if not self.rows:
            self.format()
        return super().as_text()


class CardListInfo(TextBuilder):
    """ Encapsulates text of CardListMessage """

    def __init__(self, data: dict):
        self.__cardlist: list[list[dict]] = data['cardlist']['cards']
        self.__page: int = data['cardlist']['page']
        self.__total = data['cardlist']['total']
        self.__cards: list[dict] = self.__cardlist[self.__page - 1] if self.__cardlist else []
        self.__header = f'Cards found: <b>{self.__total}</b>\n'
        super().__init__()

    def format(self):
        self.rows.append(self.__header)

        if self.__cards:
            for idx, card in enumerate(self.__cards, start=1):
                try:
                    rarity = hs_data.getrarity(name=card['rarity'])
                    ctype = hs_data.gettype(name=card['card_type'])
                    prefix = f'{ctype.emoji} {rarity.emoji}'
                except (KeyError, StopIteration):
                    prefix = '❓ ❔'
                row = md.text(
                    f'{idx}.',
                    prefix,
                    md.hlink(card['name'], url=f'{CARD_RENDER_BASE_URL}en/{card["card_id"]}.png'),
                )
                self.rows.append(row)

            self.rows.append(f'\nGet detailed information:')
        else:
            self.rows.append('Try changing the request parameters.')

    def as_text(self) -> str:
        if not self.rows:
            self.format()
        return super().as_text()


class CardDetailInfo(TextBuilder):
    """ Encapsulates text of CardDetailMessage """

    def __init__(self, data: dict):
        self.__card = data['card_detail']
        self.header = f'<b>{self.__card["name"]}</b>'
        self.id = f'ID: {self.__card["dbf_id"]}'
        self.ctype = f'<b>{self.__card["card_type"]}</b>'
        self.classes = ' | '.join(f'<b>{c}</b>' for c in self.__card["card_class"])
        self.cset = f'Set: <i>{self.__card["card_set"]}</i>'
        self.rarity = f'<b>{self.__card["rarity"]}</b>'
        self.stats = self.__make_stats()
        self.text = self.__card["text"]

        flavor = self.__card["flavor"]
        self.flavor = f'<i>{flavor}</i>' if flavor else ''

        tribe = self.__card["tribe"]
        self.tribe = f'<i>{" | ".join(tribe)}</i>' if tribe else ''

        spellschool = self.__card["spell_school"]
        self.spellschool = f'<i>{spellschool}</i>' if spellschool != '---------' else ''

        artist = self.__card["artist"]
        self.artist = f'Artist: {artist}' if artist else ''

        mechanics = self.__card["mechanic"]
        self.mechanics = f'Mechanics: {" | ".join([f"<b>{m}</b>" for m in mechanics])}' if mechanics else ''

        super().__init__()

    def format(self):
        self.rows.append(f'►►► {self.header} ◄◄◄')
        self.rows.append(self.id)

        row = f'{self.rarity} {self.ctype}'
        if self.tribe:
            row = f'{row} ({self.tribe})'
        if self.spellschool:
            row = f'{row} ({self.spellschool})'
        self.rows.append(row)

        self.rows.append(self.classes)
        self.rows.append(f'<pre>{self.stats}</pre>')
        self.rows.append(self.cset)

        if self.text or self.flavor:
            self.rows.append(' ')

        if self.text:
            self.rows.append(self.text)
        if self.flavor:
            self.rows.append(self.flavor)

        if self.text or self.flavor:
            self.rows.append(' ')

        if self.mechanics:
            self.rows.append(self.mechanics)

        if self.artist:
            self.rows.append(self.artist)

    def __make_stats(self) -> str:
        """ Return string for numeric parameters depending on card type """
        cost = self.__card.get('cost', '?')

        try:
            card_type = self.__card['card_type']
            card_type_sign = hs_data.gettype(name=card_type).sign
        except (KeyError, StopIteration):
            return f'{cost} mana ?/?'

        match card_type_sign:
            case 'M':
                attack = self.__card.get('attack', '?')
                health = self.__card.get('health', '?')
                return f'{cost} mana {attack}/{health}'
            case 'W':
                attack = self.__card.get('attack', '?')
                durability = self.__card.get('durability', '?')
                return f'{cost} mana {attack}/{durability}'
            case 'H':
                armor = self.__card.get('armor', '?')
                return f'{cost} mana {armor} armor'
            case 'S':
                return f'{cost} mana'
            case _:
                return f'{cost} mana ?/?'

    def as_text(self) -> str:
        if not self.rows:
            self.format()
        return super().as_text()


class TextInfo:

    def __init__(self, data: dict):
        self.__data = data

    @property
    def card_request(self):
        return CardRequestInfo(self.__data)

    @property
    def card_list(self):
        return CardListInfo(self.__data)

    @property
    def card_detail(self):
        return CardDetailInfo(self.__data)


class CommonMessage:
    """ Static common messages """
    START = '<b>Greetings, traveller.</b>\n\n' \
            'Available commands:\n/cards\n/decks\n/decode'
    CANCEL = '<b>All activity is cancelled. You\'re in the main menu.</b>\n\n' \
             'Available commands:\n/cards\n/decks\n/decode'
    SERVER_UNAVAILABLE = 'The server is unavailable. Please try again later'
    EMPTY_REQUEST_HINT = 'You must provide at least 1 parameter for the search'
    TOO_MANY_RESULTS_HINT_ = 'Too many results ({}). Please specify more parameters'
    UNKNOWN_ERROR = 'Unknown error :('


class InvalidInput:
    """ Hints on how to enter the parameter correctly """
    NAME_TOO_LONG = 'Name <b>must not</b> exceed <i>30</i> characters. Try again:'
    MUST_BE_NUMBER = 'This value <b>must</b> be a positive integer. Try again:'


class CardParamPrompt:
    """ Messages prompting you to enter or select parameters """
    NAME = 'Enter a <b>name</b>:'
    CTYPE = 'Select a <b>type</b>:'
    CLASSES = 'Select a <b>class</b>:'
    CSET = 'Select a <b>set</b>:'
    RARITY = 'Select a <b>rarity</b>:'
    COST = 'Enter <b>mana cost</b>:'
    ATTACK = 'Enter <b>attack</b> value:'
    HEALTH = 'Enter <b>health</b> value:'
    DURABILITY = 'Enter <b>durability</b> value:'
    ARMOR = 'Enter <b>armor</b> value:'
