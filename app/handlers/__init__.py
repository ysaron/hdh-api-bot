from aiogram import Dispatcher

from .common import register_common_handlers
from .card_request import register_card_request_handlers
from .card_response import register_card_response_handlers
from .decks import register_deck_handlers


def register_handlers(dp: Dispatcher):
    register_common_handlers(dp)
    register_card_request_handlers(dp)
    register_card_response_handlers(dp)
    register_deck_handlers(dp)
