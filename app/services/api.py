from aiohttp import ClientSession, ClientResponseError

import logging

from app.config import hs_data, BASE_API_URL
from app.exceptions import EmptyRequestError

logger = logging.getLogger('app')


class Request:
    """ API request """

    def __init__(self, endpoint: str):
        """
        :param endpoint: without first slash, f.e. `decode_deck/`
        """
        self.base_url = BASE_API_URL
        self.endpoint = endpoint

    @property
    def params(self) -> dict:
        """ Actual request parameters """
        return {}

    async def get(self):
        """
        Perform **GET** request

        :return: JSON response
        """
        async with ClientSession(raise_for_status=True) as session:
            async with session.get(f'{self.base_url}{self.endpoint}', params=self.params) as resp:
                return await resp.json()

    async def post(self, data):
        """
        Perform **POST** request

        :return: JSON response
        """
        async with ClientSession(raise_for_status=True) as session:
            async with session.post(f'{self.base_url}{self.endpoint}', data=data) as resp:
                return await resp.json(encoding='utf-8')


class RequestCards(Request):
    """ **GET card list** request """

    def __init__(self, data: dict):
        self.data = data
        super().__init__(endpoint='cards')

    @property
    def params(self) -> dict:
        clean_data = {}
        for key, value in self.data.items():
            if key not in hs_data.card_params or value is None:
                continue
            if key in hs_data.card_digit_params:
                clean_data[f'{key}_min'] = value
                clean_data[f'{key}_max'] = value
                continue
            if key == 'classes':
                value = ','.join(value)

            clean_data[key] = value
        if not clean_data:
            raise EmptyRequestError('Attempt to receive all Hearthstone cards')
        return clean_data

    async def post(self, data):
        raise NotImplementedError


class RequestSingleCard(Request):
    """ **GET single card** request """

    def __init__(self, dbf_id: int):
        super().__init__(endpoint=f'cards/{dbf_id}/')

    async def post(self, data):
        raise NotImplementedError


class RequestDecodeDeck(Request):
    """ **POST deck code** request """

    def __init__(self):
        super().__init__(endpoint='decode_deck/')

    async def get(self):
        raise NotImplementedError


class RequestDecks(Request):
    """ **GET deck list** request """

    def __init__(self, data: dict):
        self.data = data
        super().__init__(endpoint='decks/')

    async def post(self, data):
        raise NotImplementedError

    @property
    def params(self) -> dict:
        clean_data = {}
        for key, value in self.data.items():
            if key not in hs_data.deck_params or value is None:
                continue
            if key == 'deck_created_after':
                clean_data['date_after'] = self.format_date(value)
                continue
            if key == 'deck_cards':
                clean_data['cards'] = ','.join(value)
                continue

            clean_data[key] = value

        return clean_data

    @staticmethod
    def format_date(date: str) -> str:
        """
        Workaround for sending date in GET request

        :param date: date in dd.mm.yyyy format
        :return: date in mm/dd/yyyy format
        :raise ClientResponseError: if couldn't format date and perform request
        """
        try:
            date = date.split('.')
            return '/'.join([date[1], date[0], date[2]])
        except Exception as e:
            logger.warning(f"Couldn't format date {date} for GET request: {e}")
            raise ClientResponseError


class RequestSingleDeck(Request):
    """ **GET single card** request """

    def __init__(self, deck_id: int):
        super().__init__(endpoint=f'decks/{deck_id}/')

    async def post(self, data):
        raise NotImplementedError
