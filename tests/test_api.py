import pytest
from app.services.api import RequestCards


class TestRequestCards:

    @pytest.mark.asyncio
    async def test_request_card_list(self, card_request_full_data):
        request = RequestCards(card_request_full_data)

        assert request.params['classes'] == ','.join(card_request_full_data['classes'])
        assert 'cost_min' in request.params
        assert 'cost_max' in request.params
        assert request.params['cost_min'] == request.params['cost_max']
