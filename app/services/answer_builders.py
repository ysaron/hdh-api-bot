from dataclasses import dataclass

from .messages import TextInfo, CommonMessage, InvalidInput, CardParamPrompt, DeckParamPrompt
from .keyboards import Keyboard, KeyboardMarkup


@dataclass(frozen=True)
class BotAnswer:
    """
    A class that combines message data.
    The instances are unpacked into aiogram methods of sending/editing messages
    """
    text: str
    keyboard: KeyboardMarkup


class CommonAnswerBuilder:
    """ Creator of BotAnswer objects for common handlers """

    def __init__(self, data: dict):
        """
        :param data: State context
        """
        self.__data = data

    def start(self) -> BotAnswer:
        """ Create a welcome message """
        keyboard = Keyboard(self.__data).common.default()
        return BotAnswer(text=CommonMessage.START, keyboard=keyboard)

    def cancel(self) -> BotAnswer:
        """ Create simple message after all actions is cancelled """
        keyboard = Keyboard(self.__data).common.default()
        return BotAnswer(text=CommonMessage.CANCEL, keyboard=keyboard)


class CardAnswerBuilder:
    """ Creator of BotAnswer objects for card handlers """

    def __init__(self, data: dict):
        """
        :param data: State context
        """
        self.__data = data

    def request_info(self) -> BotAnswer:
        """ Create CardRequestInfoMessage """
        text = TextInfo(self.__data).card_request.as_text()
        keyboard = Keyboard(self.__data).cards.request_info()
        return BotAnswer(text=text, keyboard=keyboard)

    def wait_param(self, param: str) -> BotAnswer:
        """ Create message to receive card parameter """
        text = getattr(CardParamPrompt, param.upper())
        keyboard = Keyboard(self.__data).cards.wait_param(param)
        return BotAnswer(text=text, keyboard=keyboard)

    def invalid_param(self, param: str) -> BotAnswer:
        """ Create message to receive card parameters after an unsuccessful attempt """
        match param:
            case 'name':
                text = InvalidInput.NAME_TOO_LONG
            case 'cost' | 'attack' | 'health' | 'durability' | 'armor':
                text = InvalidInput.MUST_BE_NUMBER
            case _:
                text = 'Unknown error. Try again'

        keyboard = Keyboard(self.__data).cards.wait_param(param)
        return BotAnswer(text=text, keyboard=keyboard)

    def result_list(self) -> BotAnswer:
        """ Create paginated message with list of requested cards """
        text = TextInfo(self.__data).card_list.as_text()
        keyboard = Keyboard(self.__data).cards.result_list()
        return BotAnswer(text=text, keyboard=keyboard)

    def result_detail(self) -> BotAnswer:
        """ Create message with detail card info """
        text = TextInfo(self.__data).card_detail.as_text()
        keyboard = Keyboard(self.__data).cards.result_detail()
        return BotAnswer(text=text, keyboard=keyboard)


class DeckAnswerBuilder:
    """ Creator of BotAnswer objects for card handlers """

    def __init__(self, data: dict):
        """
        :param data: State context
        """
        self.__data = data

    @staticmethod
    def decode_prompt() -> BotAnswer:
        """ Creates a hint message for receiving the deck code """
        text = CommonMessage.DECODE_DECK_PROMPT
        return BotAnswer(text=text, keyboard=None)

    def deck_detail(self) -> BotAnswer:
        """ Creates message with deck detail info """
        text = TextInfo(self.__data).deck_detail.as_text()
        return BotAnswer(text=text, keyboard=None)

    def request_info(self) -> BotAnswer:
        """ Create DeckRequestInfoMessage """
        text = TextInfo(self.__data).deck_request.as_text()
        keyboard = Keyboard(self.__data).decks.request_info()
        return BotAnswer(text=text, keyboard=keyboard)

    def wait_param(self, param: str) -> BotAnswer:
        """ Create message to receive deck parameter """
        text = getattr(DeckParamPrompt, param.upper())
        keyboard = Keyboard(self.__data).decks.wait_param(param)
        return BotAnswer(text=text, keyboard=keyboard)

    def invalid_param(self, param: str) -> BotAnswer:
        """ Create message to receive deck parameters after an unsuccessful attempt """
        match param:
            case 'deck_created_after':
                text = InvalidInput.INVALID_DATE
            case _:
                text = 'Unknown error. Try again'

        keyboard = Keyboard(self.__data).decks.wait_param(param)
        return BotAnswer(text=text, keyboard=keyboard)

    def result_list(self) -> BotAnswer:
        """ Create paginated message with list of requested decks """
        text = TextInfo(self.__data).deck_list.as_text()
        keyboard = Keyboard(self.__data).decks.result_list()
        return BotAnswer(text=text, keyboard=keyboard)

    def result_detail(self) -> BotAnswer:
        """ Create message with detail deck info """
        text = TextInfo(self.__data).deck_detail.as_text()
        keyboard = Keyboard(self.__data).decks.result_detail()
        return BotAnswer(text=text, keyboard=keyboard)


class AnswerBuilder:
    """ Creator of BotAnswer objects """

    def __init__(self, data: dict):
        self.__data = data

    @property
    def common(self):
        """ Return creator of BotAnswers for common answers """
        return CommonAnswerBuilder(self.__data)

    @property
    def cards(self):
        """ Return creator of BotAnswers for card-related answers """
        return CardAnswerBuilder(self.__data)

    @property
    def decks(self):
        """ Return creator of BotAnswers for deck-related answers """
        return DeckAnswerBuilder(self.__data)
