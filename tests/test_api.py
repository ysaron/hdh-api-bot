import pytest
from app.services.api import RequestCards, RequestDecks


class TestRequestCards:

    @pytest.mark.asyncio
    async def test_request_card_list(self, card_request_full_data):
        request = RequestCards(card_request_full_data)

        assert request.params['classes'] == ','.join(card_request_full_data['classes'])
        assert 'cost_min' in request.params
        assert 'cost_max' in request.params
        assert request.params['cost_min'] == request.params['cost_max']


class TestRequestDecks:

    @pytest.mark.asyncio
    async def test_request_deck_list(self, deck_request_full_data):
        request = RequestDecks(deck_request_full_data)
        assert request.params['date_after'] == '01/01/2020'
        assert request.params['dformat'] == 'Wild'
        assert request.params['dclass'] == 'Warlock'
