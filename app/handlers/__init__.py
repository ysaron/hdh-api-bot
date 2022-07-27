from aiogram import Dispatcher

from .common import register_common_handlers
from .card_request import register_card_request_handlers
from .card_response import register_card_response_handlers
from .deck_decode import register_deck_decode_handlers
from .deck_request import register_deck_request_handlers
from .deck_response import register_deck_response_handlers


def register_handlers(dp: Dispatcher):
    register_common_handlers(dp)
    register_card_request_handlers(dp)
    register_card_response_handlers(dp)
    register_deck_decode_handlers(dp)
    register_deck_request_handlers(dp)
    register_deck_response_handlers(dp)
