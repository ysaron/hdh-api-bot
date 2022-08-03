from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiohttp import ClientResponseError
from aiogram.utils.exceptions import MessageNotModified

from contextlib import suppress
import logging

from app.services.keyboards import command_cd, decklist_cd
from app.services.utils import flip_page
from app.services.answer_builders import AnswerBuilder
from app.services.api import RequestSingleDeck
from app.services.messages import CommonMessage
from app.states import DeckResponse, STATES

logger = logging.getLogger('app')


async def deck_list_pages(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Called when DeckList control button is pressed """
    action = callback_data.get('action')
    match action:
        case 'left' | 'right':
            # Send another page of DeckList
            data = await state.get_data()
            try:
                deck_list = data['deck_list']
                deck_list['page'] = flip_page(action, deck_list['page'], len(deck_list['decks']))
            except KeyError as e:
                logger.error(e)
                await call.answer(CommonMessage.UNKNOWN_ERROR)
                return
            await state.update_data(deck_list=deck_list)
            data = await state.get_data()
            if data.get('deck_response_msg_id'):
                response = AnswerBuilder(data).decks.result_list()
                with suppress(MessageNotModified):
                    await call.bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=data['deck_response_msg_id'],
                        text=response.text,
                        reply_markup=response.keyboard
                    )
        case 'pages':
            # Show tooltip
            await call.answer(text='This button does nothing')
        case 'close':
            data = await state.get_data()
            on_close = data.get('on_close', 'decks_base')

            # Delete DeckList message
            await call.message.delete()

            # Set the state depending on where the decks were searched from
            await STATES[on_close].set()

            # Open keyboard again for the caused message
            for key in ['deck_request_msg_id', 'card_response_msg_id']:
                if data.get(key):
                    match on_close:
                        case 'decks_base':
                            response = AnswerBuilder(data).decks.request_info()
                        case 'cards_list':
                            response = AnswerBuilder(data).cards.result_detail()
                        case _:
                            response = AnswerBuilder(data).decks.request_info()

                    with suppress(MessageNotModified):
                        await call.bot.edit_message_reply_markup(
                            chat_id=call.message.chat.id,
                            message_id=data[key],
                            reply_markup=response.keyboard
                        )

            await state.update_data(deck_response_msg_id=None, deck_list=None, deck_detail=None, on_close=None)
        case _:
            raise ValueError(f'Unknown DeckList action: {action}')


async def deck_list_get_deck(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Called when DeckList Deck button is pressed

    Send DeckDetailMessage
    """

    deck_id = callback_data.get('id')
    if not deck_id:
        await call.answer("Something went wrong. Couldn't get detail info for this deck")
        return

    try:
        deck = await RequestSingleDeck(deck_id).get()
    except ClientResponseError as e:
        logger.error(f'HS Deck Helper API is unreachable: {e}')
        await call.answer('The server is unavailable. Please try again later.')
        return

    await state.update_data(deck_detail=deck)
    data = await state.get_data()
    if data.get('deck_response_msg_id'):
        response = AnswerBuilder(data).decks.result_detail()
        with suppress(MessageNotModified):
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=data['deck_response_msg_id'],
                text=response.text,
                reply_markup=response.keyboard
            )


async def deck_detail_back_to_list(call: types.CallbackQuery, state: FSMContext):
    """ Called when DeckDetail Back button is pressed """
    data = await state.get_data()
    if data.get('deck_response_msg_id'):
        response = AnswerBuilder(data).decks.result_list()
        with suppress(MessageNotModified):
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=data['deck_response_msg_id'],
                text=response.text,
                reply_markup=response.keyboard
            )


def register_deck_response_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        deck_list_pages,
        command_cd.filter(scope='deck_pages'),
        state=DeckResponse.list,
    )
    dp.register_callback_query_handler(
        deck_list_get_deck,
        decklist_cd.filter(action='get'),
        state=DeckResponse.list,
    )
    dp.register_callback_query_handler(
        deck_list_pages,    # Using list handler for closing detail as well
        command_cd.filter(scope='deck_detail', action='close'),
        state=DeckResponse.list,
    )
    dp.register_callback_query_handler(
        deck_detail_back_to_list,
        command_cd.filter(scope='deck_detail', action='back'),
        state=DeckResponse.list,
    )
