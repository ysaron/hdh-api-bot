from aiogram.utils import markdown as md

from app.config import hs_data, CARD_RENDER_BASE_URL, BASE_URL


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
    """ Encapsulates text of CardRequestInfoMessage """

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
        self.rows.append(self.header)
        self.rows.append(self.language)
        self.rows.append(self.collectible)
        if self.data.get('name'):
            self.rows.append(self.name.format(self.data['name']))
        if self.data.get('ctype'):
            try:
                verbose_type = hs_data.gettype(sign=self.data['ctype']).en
            except StopIteration:
                verbose_type = 'Unknown ❗️'
            self.rows.append(self.ctype.format(verbose_type))
        if self.data.get('classes'):
            verbose_class = ','.join(self.data['classes'])
            self.rows.append(self.classes.format(verbose_class))
        if self.data.get('cset'):
            self.rows.append(self.cset.format(self.data['cset']))
        if self.data.get('rarity'):
            try:
                verbose_rarity = hs_data.getrarity(sign=self.data['rarity']).en
            except StopIteration:
                verbose_rarity = 'Unknown ❗️'
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
        self.page: int = data['cardlist']['page']
        self.total = data['cardlist']['total']
        self.__cards: list[dict] = self.__cardlist[self.page - 1] if self.__cardlist else []
        self.header = f'Cards found: <b>{self.total}</b>\n'
        super().__init__()

    def format(self):
        self.rows.append(self.header)

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
            case 'L':
                health = self.__card.get('health', '?')
                return f'{cost} mana {health} health'
            case _:
                return f'{cost} mana ?/?'

    def as_text(self) -> str:
        if not self.rows:
            self.format()
        return super().as_text()


class DeckDetailInfo(TextBuilder):
    """ Encapsulates text of DeckDetailMessage """

    def __init__(self, data: dict):
        super().__init__()
        self.deck: dict = data['deck_detail']
        self.dformat = self.deck.get('deck_format', 'UNKNOWN')
        self.dclass = self.deck.get('deck_class', 'UNKNOWN')
        self.date = self.deck.get('created', '??.??.????')
        self.cards: list[dict] = self.deck['cards']
        self.string = self.deck['string']

    def format(self):
        deck_id = self.deck["id"]
        link = md.hlink(f'{self.dformat} {self.dclass} deck (id{deck_id})', url=f'{BASE_URL}/en/decks/{deck_id}')
        self.rows.append(f'<b>► ► ► {link} ◄ ◄ ◄</b>')
        self.rows.append(f'\nCreated: <b>{self.date}</b>\n')

        for card in self.cards:
            cost = card["card"]["cost"]
            url = f'{CARD_RENDER_BASE_URL}en/{card["card"]["card_id"]}.png'
            try:
                rarity = hs_data.getrarity(name=card['card']['rarity'])
                ctype = hs_data.gettype(name=card['card']['card_type'])
                prefix = f'{ctype.emoji} {rarity.emoji}'
            except (KeyError, StopIteration):
                prefix = '❓ ❔'
            row = md.text(
                f'{card["number"]}x',
                f'({cost}){"  " if cost < 10 else ""}',
                prefix,
                f'{md.hlink(card["card"]["name"], url=url)}',
            )
            self.rows.append(row)

        self.rows.append('')
        self.rows.append(md.hcode(self.string))

    def as_text(self) -> str:
        if not self.rows:
            self.format()
        return super().as_text()


class DeckRequestInfo(TextBuilder):
    """ Encapsulates text of DeckRequestInfoMessage """

    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self.header = '<b>►►► <u>Build request</u> ◄◄◄</b>'
        self.language = 'Language: <b>English</b>'
        self.dformat = 'Format: <b>{}</b>'
        self.dclass = 'Class: <b>{}</b>'
        self.created_after = 'Created after: <b>{}</b>'
        self.dcards = 'Cards:'

    def format(self):
        self.rows.append(self.header)
        self.rows.append(self.language)
        if self.data.get('dformat'):
            self.rows.append(self.dformat.format(self.data['dformat']))
        if self.data.get('dclass'):
            self.rows.append(self.dclass.format(self.data['dclass']))
        if self.data.get('deck_created_after'):
            self.rows.append(self.created_after.format(self.data['deck_created_after']))
        if self.data.get('deck_cards'):
            self.rows.append(self.dcards)
            for card in self.data['deck_cards']:
                row = md.text(
                    '-',
                    md.hlink(card['name'], url=f'{CARD_RENDER_BASE_URL}en/{card["card_id"]}.png'),
                )
                self.rows.append(row)

    def as_text(self) -> str:
        if not self.rows:
            self.format()
        return super().as_text()


class DeckListInfo(TextBuilder):
    """ Encapsulates text of DeckListMessage """

    def __init__(self, data: dict):
        self.__decklist: list[list[dict]] = data['deck_list']['decks']
        self.page: int = data['deck_list']['page']
        self.total = data['deck_list']['total']
        self.__decks: list[dict] = self.__decklist[self.page - 1] if self.__decklist else []
        self.header = f'Decks found: <b>{self.total}</b>\n'
        super().__init__()

    def format(self):
        self.rows.append(self.header)

        if self.__decks:
            for idx, deck in enumerate(self.__decks, start=1):
                row = md.text(
                    md.text(
                        f'{idx}.',
                        md.hlink(
                            f'{deck["deck_format"]} {deck["deck_class"]} deck (id{deck["id"]})',
                            url=f'{BASE_URL}/en/decks/{deck["id"]}'
                        ),
                    ),
                    md.hbold(deck["created"]),
                    md.hcode(deck["string"]),
                    sep='\n'
                )
                self.rows.append(row)
                self.rows.append(' ')

            self.rows.append(f'Get detailed information:')
        else:
            self.rows.append('Try changing the request parameters.')

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

    @property
    def deck_detail(self):
        return DeckDetailInfo(self.__data)

    @property
    def deck_request(self):
        return DeckRequestInfo(self.__data)

    @property
    def deck_list(self):
        return DeckListInfo(self.__data)


class CommonMessage:
    """ Static common messages """
    START = '<b>Greetings, traveller.</b>\n\n' \
            'Available commands:\n/cards\n/decks\n/decode'
    CANCEL = '<b>All activity is cancelled. You\'re in the main menu.</b>\n\n' \
             'Available commands:\n/cards\n/decks\n/decode'
    NEW_CARD_SEARCH = 'Starting a new card search...'
    NEW_DECK_SEARCH = 'Starting a new deck search...'
    DECODE_DECK_PROMPT = 'Send me the Hearthstone deck code, for example:\n' \
                         '<pre>AAEBAaIHBPYC0OMCt7MEv84EDYgH9bsC8OYCqssD590DqusD/u4D0/MDjfQDofQDvYAE958E/KUEAA==</pre>'
    DECODE_ERROR = f'❗️ Error: probably invalid deckstring'
    INVALID_DECKSTRING = '❗️ This deck code seems to be corrupted'
    INVALID_DECKLIST = '❗️ Couldn\'t extract the deck code'

    SERVER_UNAVAILABLE = 'The server is unavailable. Please try again later'
    EMPTY_REQUEST_HINT = 'You must provide at least 1 parameter for the search'
    TOO_MANY_RESULTS_HINT_ = 'Too many results ({}). Please specify more parameters'
    UNKNOWN_ERROR = 'Unknown error :('


class InvalidInput:
    """ Hints on how to enter the parameter correctly """
    NAME_TOO_LONG = 'Name <b>must not</b> exceed <i>30</i> characters. Try again:'
    MUST_BE_NUMBER = 'This value <b>must</b> be a positive integer. Try again:'
    INVALID_DATE = 'The date must have the format <i>dd.mm.yyyy</i> (for example, <i>15.04.2022</i>).\nTry again:'


class CardParamPrompt:
    """ Messages prompting you to enter or select card parameters """
    NAME = 'Enter the <b>name</b>:'
    CTYPE = 'Select the <b>type</b>:'
    CLASSES = 'Select the <b>class</b>:'
    CSET = 'Select the <b>set</b>:'
    RARITY = 'Select the <b>rarity</b>:'
    COST = 'Enter the <b>mana cost</b>:'
    ATTACK = 'Enter the <b>attack</b> value:'
    HEALTH = 'Enter the <b>health</b> value:'
    DURABILITY = 'Enter the <b>durability</b> value:'
    ARMOR = 'Enter the <b>armor</b> value:'


class DeckParamPrompt:
    """ Messages prompting you to enter or select deck parameters """
    DFORMAT = 'Select the <b>format</b>:'
    DCLASS = 'Select the <b>class</b>:'
    DECK_CREATED_AFTER = 'Enter the date in the format <i>dd.mm.yyyy</i>'
