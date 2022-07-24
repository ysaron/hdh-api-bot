from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters

import logging

from app.services.answer_builders import AnswerBuilder
from app.services.messages import CommonMessage
from app.services.utils import is_valid_deckstring, extract_deckstring, deck_decode
from app.exceptions import DeckstringError

logger = logging.getLogger('app')


async def deck_search_start(message: types.Message, state: FSMContext):
    await message.reply(text='Coming soon!')


async def deck_decode_start(message: types.Message, state: FSMContext):
    """ Prompt to enter the deck code """
    answer = AnswerBuilder({}).decks.decode_prompt()
    await message.reply(text=answer.text)


async def deck_decode_from_deckstring(message: types.Message, state: FSMContext):
    """ Check deckstring and call ``deck_decode`` """
    if not is_valid_deckstring(message.text):
        await message.reply(CommonMessage.INVALID_DECKSTRING)
        return

    await deck_decode(message, state, deckstring=message.text)


async def deck_decode_from_decklist(message: types.Message, state: FSMContext):
    """ Extract deckstring and call ``deck_decode`` """
    try:
        deckstring = extract_deckstring(decklist=message.text)
    except DeckstringError:
        await message.reply(CommonMessage.INVALID_DECKLIST)
        return

    await deck_decode(message, state, deckstring=deckstring)


def register_deck_handlers(dp: Dispatcher):
    dp.register_message_handler(deck_search_start, commands='decks', state='*')
    dp.register_message_handler(
        deck_search_start,
        filters.Text(equals='decks', ignore_case=True),
        state='*',
    )

    dp.register_message_handler(deck_decode_start, commands='decode', state='*')
    dp.register_message_handler(
        deck_decode_start,
        filters.Text(equals='decode deckstring', ignore_case=True),
        state='*',
    )

    dp.register_message_handler(
        deck_decode_from_deckstring,
        filters.Text(startswith='AAE'),
        state='*',
    )
    dp.register_message_handler(
        deck_decode_from_decklist,
        filters.Text(startswith='###'),
        state='*',
    )
