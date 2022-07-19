from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters


async def deck_search_start(message: types.Message, state: FSMContext):
    await message.reply(text='Coming soon!')


async def deck_decode_start(message: types.Message, state: FSMContext):
    await message.reply(text='Coming soon!')


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
