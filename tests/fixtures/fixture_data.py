import pytest
import ujson

from app.services.messages import CardRequestInfo, CardListInfo, CardDetailInfo
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
    return CardRequestInfo(data=card_request_data)


@pytest.fixture
def card_list_info_obj(card_list_data):
    return CardListInfo(data=card_list_data)


@pytest.fixture
def card_detail_info_obj(card_detail_data):
    return CardDetailInfo(data=card_detail_data)
