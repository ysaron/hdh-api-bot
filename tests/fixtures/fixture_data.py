import pytest
import ujson

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove

from app.services.messages import TextInfo, CardRequestInfo, CardListInfo, CardDetailInfo, DeckDetailInfo
from app.services.keyboards import Keyboard, CommonKeyboardBuilder, CardKeyboardBuilder
from app.config import BASE_DIR


DATA_DIR = BASE_DIR / 'tests' / 'fixtures' / 'data'


@pytest.fixture
def card_request_data() -> dict:
    """ Data used for build and perform request to cardlist endpoint """
    return {
        'classes': ['Demon Hunter', 'Mage'],
        'armor': None,
        'ctype': 'M',
        'rarity': 'C',
        'attack': '4',
        'health': '3',
        'name': 'A',
        'cset': 'Voyage to the Sunken City',
        'cost': '3',
    }


@pytest.fixture
def card_list_data() -> dict:
    """ Data used for building cardlist response """
    with open(DATA_DIR / 'cardlist_fixture.json', 'r', encoding='utf-8') as f:
        return ujson.load(f)


@pytest.fixture
def card_detail_data() -> dict:
    """ Data used for building carddetail response """
    with open(DATA_DIR / 'carddetail_fixture.json', 'r', encoding='utf-8') as f:
        return ujson.load(f)


@pytest.fixture
def card_request_full_data(card_request_data) -> dict:
    """ Full context data for build-request handlers """
    return card_request_data | {'request_msg_id': 1111, 'prompt_msg_id': 1112}


@pytest.fixture
def card_list_full_data(card_list_data) -> dict:
    """ Full context data for cardlist handlers """
    return card_list_data | {'response_msg_id': 1113}


@pytest.fixture
def card_detail_full_data(card_detail_data) -> dict:
    """ Full context data for carddetail handlers """
    return card_detail_data | {'response_msg_id': 1113}


@pytest.fixture
def card_request_info_obj(card_request_data) -> CardRequestInfo:
    return TextInfo(data=card_request_data).card_request


@pytest.fixture
def card_list_info_obj(card_list_data) -> CardListInfo:
    return TextInfo(data=card_list_data).card_list


@pytest.fixture
def card_detail_info_obj(card_detail_data) -> CardDetailInfo:
    return TextInfo(data=card_detail_data).card_detail


@pytest.fixture
def deck_detail_info_obj(deck_detail_data) -> DeckDetailInfo:
    return TextInfo(data=deck_detail_data).deck_detail


@pytest.fixture
def reply_keyboard():
    """ Empty Telegram Reply Keyboard """
    return ReplyKeyboardMarkup()


@pytest.fixture
def remove_keyboard():
    return ReplyKeyboardRemove()


@pytest.fixture
def inline_keyboard():
    """ Empty Telegram Inline Keyboard """
    return InlineKeyboardMarkup()


@pytest.fixture
def common_keyboard_builder_obj(card_request_data) -> CommonKeyboardBuilder:
    return Keyboard(data=card_request_data).common


@pytest.fixture
def card_request_keyboard_builder_obj(card_request_data) -> CardKeyboardBuilder:
    return Keyboard(data=card_request_data).cards


@pytest.fixture
def card_list_keyboard_builder_obj(card_list_data) -> CardKeyboardBuilder:
    return Keyboard(data=card_list_data).cards


@pytest.fixture
def card_detail_keyboard_builder_obj(card_detail_data) -> CardKeyboardBuilder:
    return Keyboard(data=card_detail_data).cards


@pytest.fixture
def pure_deckstring() -> str:
    return 'AAEBAZ/HAgjSwQLo0ALY4wKC9wKh/gKspQOnywOX7wQQ5QSCtALRwQLYw' \
           'QLQ/gLxgAPmiAPrigOTugObugPi3gP73wPK4QOtigTUrASktgQA'


@pytest.fixture
def decklist_from_game() -> str:
    return """
        ### Колода
        # Класс: Жрец
        # Формат: Вольный
        #
        # 2x (0) Переворот
        # 1x (1) Бальзамирование
        # 2x (1) Обновление
        # 2x (1) Подопытный
        # 1x (1) Связующее исцеление
        # 2x (1) Слово силы: Щит
        # 2x (2) Любовь к тени
        # 2x (2) Прозрение
        # 2x (2) Сетеккская ворожея
        # 2x (2) Сияющий элементаль
        # 1x (2) Смертозвон
        # 2x (2) Спиритизм
        # 2x (2) Темные видения
        # 2x (3) Гадание по руке
        # 1x (3) Дар сияния
        # 1x (3) Душа дракона
        # 2x (3) Назманийская колдунья
        # 1x (3) Оживший кошмар
        # 1x (3) Принц Ренатал
        # 2x (3) Служанка
        # 2x (4) Светозарный дракон Пустоты
        # 1x (7) Ментальный крик
        # 2x (12) Волшебный великан
        # 2x (12) Могильный ужас
        # 
        AAEBAZ/HAgjSwQLo0ALY4wKC9wKh/gKspQOnywOX7wQQ5QSCtALRwQLYwQLQ/gLxgAPmiAPrigOTugObugPi3gP73wPK4QOtigTUrASktgQA
        # 
        # Чтобы использовать эту колоду, скопируйте ее в буфер обмена и создайте новую колоду в Hearthstone.
    """


@pytest.fixture
def deck_detail_data() -> dict:
    """ Data used for building carddetail response """
    with open(DATA_DIR / 'deckdetail_fixture.json', 'r', encoding='utf-8') as f:
        return ujson.load(f)


@pytest.fixture
def deck_detail_full_data(deck_detail_data) -> dict:
    """ Full context data for build-request handlers """
    return deck_detail_data | {'request_msg_id': 1111, 'prompt_msg_id': 1112, 'response_msg_id': 1113}
