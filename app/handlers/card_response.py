from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiohttp import ClientResponseError
from aiogram.utils.exceptions import MessageNotModified

from contextlib import suppress
import logging

from app.services.keyboards import command_cd, cardlist_cd
from app.services.utils import flip_page
from app.services.answer_builders import AnswerBuilder
from app.services.api import RequestSingleCard
from app.services.messages import CommonMessage
from app.states.cards import BuildCardRequest, CardResponse

logger = logging.getLogger('app')


async def card_list_pages(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Called when CardList Control button is pressed """

    action = callback_data.get('action')
    match action:
        case 'left' | 'right':
            # Send another page of CardList
            data = await state.get_data()
            try:
                cardlist = data['cardlist']
                cardlist['page'] = flip_page(action, cardlist['page'], len(cardlist['cards']))
            except KeyError as e:
                logger.error(e)
                await call.answer(CommonMessage.UNKNOWN_ERROR)
                return
            await state.update_data(cardlist=cardlist)
            data = await state.get_data()
            if data.get('response_msg_id'):
                response = AnswerBuilder(data).cards.result_list()
                with suppress(MessageNotModified):
                    await call.bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=data['response_msg_id'],
                        text=response.text,
                        reply_markup=response.keyboard
                    )
        case 'pages':
            # Show tooltip
            await call.answer(text='This button does nothing')
        case 'close':
            # Delete CardList message
            await call.message.delete()
            await BuildCardRequest.base.set()
            await state.update_data(response_msg_id=None)
        case _:
            raise ValueError(f'Unknown CardList action: {action}')


async def card_list_get_card(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """
    Called when CardList Control button is pressed
    Send CardDetailMessage
    """

    dbf_id = callback_data.get('id')
    if not dbf_id:
        await call.answer("Something went wrong. Couldn't get detail info for this card")
        return

    try:
        card = await RequestSingleCard(dbf_id).perform()
    except ClientResponseError as e:
        logger.error(f'HS Deck Helper API is unreachable: {e}')
        await call.answer('The server is unavailable. Please try again later.')
        return

    await state.update_data(card_detail=card)
    data = await state.get_data()
    if data.get('response_msg_id'):
        response = AnswerBuilder(data).cards.result_detail()
        with suppress(MessageNotModified):
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=data['response_msg_id'],
                text=response.text,
                reply_markup=response.keyboard
            )


async def card_detail_back_to_list(call: types.CallbackQuery, state: FSMContext):
    """ Called when CardDetail Back button is pressed """
    data = await state.get_data()
    if data.get('response_msg_id'):
        response = AnswerBuilder(data).cards.result_list()
        with suppress(MessageNotModified):
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=data['response_msg_id'],
                text=response.text,
                reply_markup=response.keyboard
            )


async def card_detail_find_decks(call: types.CallbackQuery, state: FSMContext):
    """ Search decks with current card """
    data = await state.get_data()
    card = data.get('card_detail')
    if not card:
        await call.answer(CommonMessage.UNKNOWN_ERROR)
        return
    await call.answer(f'Coming soon!')


def register_card_response_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        card_list_pages,
        command_cd.filter(scope='card_pages'),
        state=CardResponse.list,
    )
    dp.register_callback_query_handler(
        card_list_get_card,
        cardlist_cd.filter(action='get'),
        state=CardResponse.list,
    )
    dp.register_callback_query_handler(
        card_list_pages,    # Using list handler for closing detail as well
        command_cd.filter(scope='card_detail', action='close'),
        state=CardResponse.list,
    )
    dp.register_callback_query_handler(
        card_detail_back_to_list,
        command_cd.filter(scope='card_detail', action='back'),
        state=CardResponse.list,
    )

    dp.register_callback_query_handler(
        card_detail_find_decks,
        command_cd.filter(scope='card_detail', action='decks'),
        state=CardResponse.list,
    )
