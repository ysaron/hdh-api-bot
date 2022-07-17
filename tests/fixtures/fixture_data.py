import pytest
import ujson

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

from app.services.messages import TextInfo
from app.services.keyboards import Keyboard
from app.config import BASE_DIR


DATA_DIR = BASE_DIR / 'tests' / 'fixtures' / 'data'


@pytest.fixture
def card_request_data():
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
def card_list_data():
    with open(DATA_DIR / 'cardlist_fixture.json', 'r', encoding='utf-8') as f:
        return ujson.load(f)


@pytest.fixture
def card_detail_data():
    with open(DATA_DIR / 'carddetail_fixture.json', 'r', encoding='utf-8') as f:
        return ujson.load(f)


@pytest.fixture
def card_request_info_obj(card_request_data):
    return TextInfo(data=card_request_data).card_request


@pytest.fixture
def card_list_info_obj(card_list_data):
    return TextInfo(data=card_list_data).card_list


@pytest.fixture
def card_detail_info_obj(card_detail_data):
    return TextInfo(data=card_detail_data).card_detail


@pytest.fixture
def reply_keyboard():
    return ReplyKeyboardMarkup()


@pytest.fixture
def inline_keyboard():
    return InlineKeyboardMarkup()


@pytest.fixture
def common_keyboard_builder_obj(card_request_data):
    return Keyboard(data=card_request_data).common


@pytest.fixture
def card_request_keyboard_builder_obj(card_request_data):
    return Keyboard(data=card_request_data).cards


@pytest.fixture
def card_list_keyboard_builder_obj(card_list_data):
    return Keyboard(data=card_list_data).cards


@pytest.fixture
def card_detail_keyboard_builder_obj(card_detail_data):
    return Keyboard(data=card_detail_data).cards
