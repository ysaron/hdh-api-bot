from aiohttp import ClientSession

from app.config import hs_data, BASE_URL
from app.exceptions import EmptyRequestError


class Request:
    """ API request """

    def __init__(self, endpoint: str):
        self.base_url = BASE_URL
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
    """ **GET card_list** request """

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
    """ `GET single_card` request """

    def __init__(self, dbf_id: int):
        super().__init__(endpoint=f'cards/{dbf_id}/')

    async def post(self, data):
        raise NotImplementedError


class RequestDecodeDeck(Request):
    """ `POST deck code` request """

    def __init__(self):
        super().__init__(endpoint='decode_deck/')

    async def get(self):
        raise NotImplementedError
