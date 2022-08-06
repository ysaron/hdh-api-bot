from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters
from aiogram.utils.exceptions import MessageNotModified, MessageToEditNotFound, BadRequest
from aiohttp import ClientResponseError

import logging
from contextlib import suppress

from app.services.answer_builders import AnswerBuilder
from app.services.messages import CommonMessage
from app.services.keyboards import command_cd, deckparam_cd, cardlist_cd
from app.services.utils import clear_prompt, check_date, clear_all, paginate_list, card_in_query
from app.services.api import RequestDecks
from app.states import BuildDeckRequest, DeckResponse, CardResponse, BuildCardRequest
from app.config import hs_data, MAX_DECKS_IN_RESPONSE

logger = logging.getLogger('app')


async def update_deck_request(message: types.Message, state: FSMContext, request_data: dict):
    """ Update request and DeckRequestInfoMessage """

    data = await state.get_data()
    answer = AnswerBuilder(data).decks.request_info()

    if request_data.get('deck_request_msg_id'):
        with suppress(MessageNotModified, MessageToEditNotFound):
            await message.bot.edit_message_text(
                answer.text,
                chat_id=message.chat.id,
                message_id=request_data['deck_request_msg_id'],
                reply_markup=answer.keyboard,
            )


async def deck_search_start(message: types.Message, state: FSMContext):
    """ Start a new deck request, send DeckRequestInfoMessage """
    data = await state.get_data()
    answer = AnswerBuilder(data).decks.request_info()

    # To remove ReplyKeyboard
    await message.answer(text=CommonMessage.NEW_DECK_SEARCH, reply_markup=types.ReplyKeyboardRemove())

    request_message = await message.answer(text=answer.text, reply_markup=answer.keyboard)
    await BuildDeckRequest.base.set()
    await state.update_data(deck_request_msg_id=request_message.message_id, on_close='')


async def deck_search_param_cancel(call: types.CallbackQuery, state: FSMContext):
    """ Return to DeckRequestInfoMessage without changes """
    await call.message.delete()
    await state.update_data(deck_prompt_msg_id=None)
    await BuildDeckRequest.base.set()


async def deck_search_param_clear(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Remove selected parameter from the deck request """
    await call.message.delete()
    await BuildDeckRequest.base.set()

    param = callback_data['param']
    await state.update_data({param: None, 'deck_prompt_msg_id': None})

    data = await state.get_data()
    await update_deck_request(call.message, state, data)


async def deck_search_format_input(call: types.CallbackQuery, state: FSMContext):
    """ Prepare to receive a deck format """
    data = await state.get_data()
    answer = AnswerBuilder(data).decks.wait_param('dformat')
    prompt = await call.message.reply(answer.text, reply_markup=answer.keyboard)
    await BuildDeckRequest.wait_format.set()
    await state.update_data(deck_prompt_msg_id=prompt.message_id)
    await call.answer()


async def deck_search_format_chosen(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Process the selected deck format """
    data = await state.get_data()
    await clear_prompt(call.message, data, state)
    await BuildDeckRequest.base.set()
    await state.update_data(dformat=callback_data['param'])
    await update_deck_request(call.message, state, data)


async def deck_search_class_input(call: types.CallbackQuery, state: FSMContext):
    """ Prepare to receive a deck class """
    data = await state.get_data()
    answer = AnswerBuilder(data).decks.wait_param('dclass')
    prompt = await call.message.reply(answer.text, reply_markup=answer.keyboard)
    await BuildDeckRequest.wait_class.set()
    await state.update_data(deck_prompt_msg_id=prompt.message_id)
    await call.answer()


async def deck_search_class_chosen(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Process the selected deck class """
    data = await state.get_data()
    await clear_prompt(call.message, data, state)
    await BuildDeckRequest.base.set()
    await state.update_data(dclass=callback_data['param'])
    await update_deck_request(call.message, state, data)


async def deck_search_date_input(call: types.CallbackQuery, state: FSMContext):
    """ Prepare to receive a deck creation date """
    data = await state.get_data()
    answer = AnswerBuilder(data).decks.wait_param('deck_created_after')
    prompt = await call.message.reply(answer.text, reply_markup=answer.keyboard)
    await BuildDeckRequest.wait_date.set()
    await state.update_data(deck_prompt_msg_id=prompt.message_id)
    await call.answer()


async def deck_search_date_entered(message: types.Message, state: FSMContext):
    """ Process the entered deck creation date """
    data = await state.get_data()
    await message.delete()

    if check_date(message.text):
        await clear_prompt(message, data, state)
        await BuildDeckRequest.base.set()
        await state.update_data(deck_created_after=message.text)
        await update_deck_request(message, state, data)
    else:
        if data.get('deck_prompt_msg_id'):
            answer = AnswerBuilder(data).decks.invalid_param('deck_created_after')
            with suppress(MessageNotModified):
                await message.bot.edit_message_text(
                    answer.text,
                    chat_id=message.chat.id,
                    message_id=data['deck_prompt_msg_id'],
                    reply_markup=answer.keyboard,
                )


async def deck_search_add_card(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Add current card data to deck request, close Card Detail Info """
    data = await state.get_data()
    query_cards = data.get('deck_cards')
    current_card = data.get('card_detail')
    if query_cards is None:
        query_cards = []

    if not current_card:
        logger.error("Couldn't add current card to query")
        return

    if not card_in_query(current_card, query_cards):
        new_query_card = {
            'id': current_card['dbf_id'],
            'card_id': current_card['card_id'],
            'name': current_card['name'],
        }
        query_cards.append(new_query_card)

    await state.update_data(deck_cards=query_cards, card_response_msg_id=None)
    data = await state.get_data()

    # Update DeckRequestInfo
    if data.get('deck_request_msg_id'):
        response = AnswerBuilder(data).decks.request_info()
        with suppress(MessageNotModified):
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=data['deck_request_msg_id'],
                text=response.text,
                reply_markup=response.keyboard
            )

    # Back to card search
    await call.message.delete()
    await BuildCardRequest.base.set()
    if data.get('card_request_msg_id'):
        response = AnswerBuilder(data).cards.request_info()
        with suppress(MessageNotModified):
            await call.bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=data['card_request_msg_id'],
                reply_markup=response.keyboard
            )


async def deck_search_language_input(call: types.CallbackQuery):
    """ Prepare to receive a language """
    await call.answer('Currently, only English is available')


async def deck_search_close(call: types.CallbackQuery, state: FSMContext):
    """ Called when Close button of DeckRequestInfoMessage is pressed """
    await clear_all(call.message, state)
    data = await state.get_data()
    answer = AnswerBuilder(data).common.cancel()
    await call.bot.send_message(
        chat_id=call.message.chat.id,
        text=answer.text,
        reply_markup=answer.keyboard,
    )


async def deck_search_clear(call: types.CallbackQuery, state: FSMContext):
    """
    Clear all deck request parameters

    Called when Clear button of DeckRequestInfoMessage is pressed
    """
    await state.update_data(**dict.fromkeys(hs_data.deck_params, None))
    data = await state.get_data()
    await call.answer()
    await update_deck_request(call.message, state, data)


async def request_decks(call: types.CallbackQuery, state: FSMContext):
    """ Perform request, send deck_list """
    data = await state.get_data()
    try:
        decks = await RequestDecks(data).get()
    except ClientResponseError as e:
        logger.error(f'HS Deck Helper API is unreachable: {e}')
        await call.answer(CommonMessage.SERVER_UNAVAILABLE)
        return

    amount = len(decks)
    if amount > MAX_DECKS_IN_RESPONSE:
        await call.answer(CommonMessage.TOO_MANY_RESULTS_HINT_.format(amount))
        return

    decks = list(paginate_list(decks, 9))

    await state.update_data(deck_list={'decks': decks, 'page': 1, 'total': amount})

    data = await state.get_data()
    response = AnswerBuilder(data).decks.result_list()

    try:
        resp_msg = await call.message.reply(text=response.text, reply_markup=response.keyboard)

        # Close keyboard for DeckRequestInfoMessage
        await call.message.edit_reply_markup()
    except BadRequest:
        resp_msg = await call.bot.send_message(
            chat_id=call.from_user.id,
            text=response.text,
            reply_markup=response.keyboard,
        )
    await state.update_data(deck_response_msg_id=resp_msg.message_id)
    await DeckResponse.list.set()
    await call.answer()


async def deck_search(call: types.CallbackQuery, state: FSMContext):
    """ Search decks from Deck Request """

    await state.update_data(on_close='decks_base')
    await request_decks(call, state)


async def deck_search_from_card_detail(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Search decks from Card Detail """
    dbf_id = callback_data.get('id')
    if not dbf_id:
        await call.answer("Something went wrong. Couldn't get card data")
        return

    data = await state.get_data()
    current_card = data.get('card_detail')
    query_card = {
        'id': current_card['dbf_id'],
        'card_id': current_card['card_id'],
        'name': current_card['name'],
    }
    await state.update_data(deck_cards=[query_card], deck_created_after=None, dformat=None, dclass=None,
                            on_close='cards_list')
    await request_decks(call, state)


def register_deck_request_handlers(dp: Dispatcher):
    dp.register_message_handler(deck_search_start, commands='decks', state='*')
    dp.register_message_handler(
        deck_search_start,
        filters.Text(equals='decks', ignore_case=True),
        state='*',
    )

    dp.register_callback_query_handler(
        deck_search_close,
        command_cd.filter(scope='deck_request', action='close'),
        state=BuildDeckRequest.base,
    )
    dp.register_callback_query_handler(
        deck_search_clear,
        command_cd.filter(scope='deck_request', action='clear'),
        state=BuildDeckRequest.base,
    )
    dp.register_callback_query_handler(
        deck_search,
        command_cd.filter(scope='deck_request', action='request'),
        state=BuildDeckRequest.base,
    )
    dp.register_callback_query_handler(
        deck_search_from_card_detail,
        cardlist_cd.filter(action='getdecks'),
        state=CardResponse.list,
    )
    dp.register_callback_query_handler(
        deck_search_format_input,
        deckparam_cd.filter(param='dformat', action='add'),
        state=BuildDeckRequest.base,
    )
    dp.register_callback_query_handler(
        deck_search_class_input,
        deckparam_cd.filter(param='dclass', action='add'),
        state=BuildDeckRequest.base,
    )
    dp.register_callback_query_handler(
        deck_search_date_input,
        deckparam_cd.filter(param='deck_created_after', action='add'),
        state=BuildDeckRequest.base,
    )
    dp.register_callback_query_handler(
        deck_search_add_card,
        cardlist_cd.filter(action='addcard'),
        state=CardResponse.list,
    )
    dp.register_callback_query_handler(
        deck_search_language_input,
        deckparam_cd.filter(param='language', action='add'),
        state=BuildDeckRequest.base,
    )
    dp.register_callback_query_handler(
        deck_search_param_cancel,
        deckparam_cd.filter(action='cancel'),
        state='*',
    )
    dp.register_callback_query_handler(
        deck_search_param_clear,
        deckparam_cd.filter(action='clear'),
        state='*',
    )
    dp.register_callback_query_handler(
        deck_search_format_chosen,
        deckparam_cd.filter(action='submit'),
        state=BuildDeckRequest.wait_format,
    )
    dp.register_callback_query_handler(
        deck_search_class_chosen,
        deckparam_cd.filter(action='submit'),
        state=BuildDeckRequest.wait_class,
    )
    dp.register_message_handler(
        deck_search_date_entered,
        state=BuildDeckRequest.wait_date,
    )
