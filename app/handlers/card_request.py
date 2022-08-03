from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiohttp import ClientResponseError
from aiogram.utils.exceptions import MessageNotModified, MessageToEditNotFound, BadRequest

from contextlib import suppress
import logging

from app.services.keyboards import cardparam_cd, command_cd
from app.services.utils import is_positive_integer, clear_all, clear_prompt, paginate_list, check_card_name
from app.services.answer_builders import AnswerBuilder
from app.services.api import RequestCards
from app.services.messages import CommonMessage
from app.states import BuildCardRequest, WaitCardNumericParam, CardResponse
from app.config import hs_data, MAX_CARDS_IN_RESPONSE
from app.exceptions import EmptyRequestError

logger = logging.getLogger('app')


async def update_card_request(message: types.Message, state: FSMContext, request_data: dict):
    """ Update request and CardRequestInfoMessage """

    data = await state.get_data()
    answer = AnswerBuilder(data).cards.request_info()

    if request_data.get('card_request_msg_id'):
        with suppress(MessageNotModified, MessageToEditNotFound):
            await message.bot.edit_message_text(
                answer.text,
                chat_id=message.chat.id,
                message_id=request_data['card_request_msg_id'],
                reply_markup=answer.keyboard,
            )


async def card_search_start(message: types.Message, state: FSMContext):
    """ Start a new card request, send CardRequestInfoMessage """
    data = await state.get_data()
    answer = AnswerBuilder(data).cards.request_info()

    # To remove ReplyKeyboard
    await message.answer(text=CommonMessage.NEW_CARD_SEARCH, reply_markup=types.ReplyKeyboardRemove())

    request_message = await message.answer(text=answer.text, reply_markup=answer.keyboard)
    await BuildCardRequest.base.set()
    await state.update_data(card_request_msg_id=request_message.message_id)


async def card_search_param_cancel(call: types.CallbackQuery, state: FSMContext):
    """ Return to CardRequestInfoMessage without changes """
    await call.message.delete()
    await state.update_data(card_prompt_msg_id=None)
    await BuildCardRequest.base.set()


async def card_search_param_clear(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Remove selected parameter from the card request """
    await call.message.delete()
    await BuildCardRequest.base.set()

    param = callback_data['param']
    await state.update_data({param: None, 'card_prompt_msg_id': None})

    data = await state.get_data()
    await update_card_request(call.message, state, data)


async def card_search_name_input(call: types.CallbackQuery, state: FSMContext):
    """ Prepare to receive a card name """
    data = await state.get_data()
    answer = AnswerBuilder(data).cards.wait_param('name')
    prompt = await call.message.reply(answer.text, reply_markup=answer.keyboard)
    await BuildCardRequest.wait_name.set()
    await state.update_data(card_prompt_msg_id=prompt.message_id)
    await call.answer()


async def card_search_name_entered(message: types.Message, state: FSMContext):
    """ Process the entered card name """
    data = await state.get_data()
    await message.delete()

    if check_card_name(message.text):
        await clear_prompt(message, data, state)
        await BuildCardRequest.base.set()
        await state.update_data(name=message.text)

        await update_card_request(message, state, data)
    else:
        if data.get('card_prompt_msg_id'):
            answer = AnswerBuilder(data).cards.invalid_param('name')
            with suppress(MessageNotModified):
                await message.bot.edit_message_text(
                    answer.text,
                    chat_id=message.chat.id,
                    message_id=data['card_prompt_msg_id'],
                    reply_markup=answer.keyboard,
                )


async def card_search_type_input(call: types.CallbackQuery, state: FSMContext):
    """ Prepare to receive a card type """
    data = await state.get_data()
    answer = AnswerBuilder(data).cards.wait_param('ctype')
    prompt = await call.message.reply(answer.text, reply_markup=answer.keyboard)
    await BuildCardRequest.wait_type.set()
    await state.update_data(card_prompt_msg_id=prompt.message_id)
    await call.answer()


async def card_search_type_chosen(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Process the selected card type """
    data = await state.get_data()
    type_sign = callback_data['param']

    # Processing the type change after entering numerical parameters
    match type_sign:
        case 'M':
            await state.update_data(armor=None, durability=None)
        case 'W':
            await state.update_data(armor=None, health=None)
        case 'S':
            await state.update_data(armor=None, durability=None, attack=None, health=None)
        case 'H':
            await state.update_data(attack=None, health=None, durability=None)
        case 'L':
            await state.update_data(attack=None, armor=None, durability=None)

    await clear_prompt(call.message, data, state)
    await BuildCardRequest.base.set()
    await state.update_data(ctype=type_sign)

    await update_card_request(call.message, state, data)


async def card_search_class_input(call: types.CallbackQuery, state: FSMContext):
    """ Prepare to receive a class """
    data = await state.get_data()
    answer = AnswerBuilder(data).cards.wait_param('classes')
    prompt = await call.message.reply(answer.text, reply_markup=answer.keyboard)
    await BuildCardRequest.wait_class.set()
    await state.update_data(card_prompt_msg_id=prompt.message_id)
    await call.answer()


async def card_search_class_chosen(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Process the selected card class """
    data = await state.get_data()

    # not `default=[]`, because `data['classes']` may not exist and may be None
    current_classes = data.get('classes')
    if current_classes is None:
        current_classes = []

    if callback_data['param'] not in current_classes:
        current_classes.append(callback_data['param'])
    await clear_prompt(call.message, data, state)
    await BuildCardRequest.base.set()
    await state.update_data(classes=current_classes)

    await update_card_request(call.message, state, data)


async def card_search_set_input(call: types.CallbackQuery, state: FSMContext):
    """ Prepare to receive a card set """
    data = await state.get_data()
    answer = AnswerBuilder(data).cards.wait_param('cset')
    prompt = await call.message.reply(answer.text, reply_markup=answer.keyboard)
    await BuildCardRequest.wait_set.set()
    await state.update_data(card_prompt_msg_id=prompt.message_id)
    await call.answer()


async def card_search_set_chosen(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Process the selected card set """
    data = await state.get_data()
    await clear_prompt(call.message, data, state)
    await BuildCardRequest.base.set()
    await state.update_data(cset=callback_data['param'])

    await update_card_request(call.message, state, data)


async def card_search_rarity_input(call: types.CallbackQuery, state: FSMContext):
    """ Prepare to receive a card rarity """
    data = await state.get_data()
    answer = AnswerBuilder(data).cards.wait_param('rarity')
    prompt = await call.message.reply(answer.text, reply_markup=answer.keyboard)
    await BuildCardRequest.wait_rarity.set()
    await state.update_data(card_prompt_msg_id=prompt.message_id)
    await call.answer()


async def card_search_rarity_chosen(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Process the selected card rarity """
    data = await state.get_data()
    await clear_prompt(call.message, data, state)
    await BuildCardRequest.base.set()
    await state.update_data(rarity=callback_data['param'])

    await update_card_request(call.message, state, data)


async def card_search_digit_param_input(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """ Prepare to receive a numeric request parameter """
    data = await state.get_data()
    match callback_data.get('param'):
        case 'cost':
            answer = AnswerBuilder(data).cards.wait_param('cost')
            await WaitCardNumericParam.cost.set()
        case 'attack':
            answer = AnswerBuilder(data).cards.wait_param('attack')
            await WaitCardNumericParam.attack.set()
        case 'health':
            answer = AnswerBuilder(data).cards.wait_param('health')
            await WaitCardNumericParam.health.set()
        case 'durability':
            answer = AnswerBuilder(data).cards.wait_param('durability')
            await WaitCardNumericParam.durability.set()
        case 'armor':
            answer = AnswerBuilder(data).cards.wait_param('armor')
            await WaitCardNumericParam.armor.set()
        case _:
            return

    prompt = await call.message.reply(answer.text, reply_markup=answer.keyboard)

    await state.update_data(card_prompt_msg_id=prompt.message_id)
    await call.answer()


async def card_search_digit_param_entered(message: types.Message, state: FSMContext):
    """ Process the entered numeric parameter """
    param = (await state.get_state()).split(':')[-1]

    data = await state.get_data()
    if is_positive_integer(message.text):
        await clear_prompt(message, data, state)
        await BuildCardRequest.base.set()
        await state.update_data({param: message.text})

        await update_card_request(message, state, data)
    else:
        if data.get('card_prompt_msg_id'):
            answer = AnswerBuilder(data).cards.invalid_param(param)
            with suppress(MessageNotModified):
                await message.bot.edit_message_text(
                    answer.text,
                    chat_id=message.chat.id,
                    message_id=data['card_prompt_msg_id'],
                    reply_markup=answer.keyboard,
                )
    await message.delete()


async def card_search_language_input(call: types.CallbackQuery):
    """ Prepare to receive a language """
    await call.answer('Currently, only English is available')


async def card_search_collectible_input(call: types.CallbackQuery):
    """ Prepare to receive a collectibility """
    await call.answer('Coming soon. Or not')


# ----------------------------------------------------------------------------------------------------------


async def card_search_close(call: types.CallbackQuery, state: FSMContext):
    """ Called when Close button of CardRequestInfoMessage is pressed """
    await clear_all(call.message, state)
    data = await state.get_data()
    answer = AnswerBuilder(data).common.cancel()
    await call.bot.send_message(
        chat_id=call.message.chat.id,
        text=answer.text,
        reply_markup=answer.keyboard,
    )


async def card_search_clear(call: types.CallbackQuery, state: FSMContext):
    """
    Clear all card request parameters

    Called when Clear button of CardRequestInfoMessage is pressed
    """
    await state.update_data(**dict.fromkeys(hs_data.card_params, None))
    data = await state.get_data()
    await call.answer()
    await update_card_request(call.message, state, data)


async def card_search(call: types.CallbackQuery, state: FSMContext):
    """
    Perform API request with stored parameters

    Send formatted response
    """

    data = await state.get_data()

    try:
        cards = await RequestCards(data).get()
    except ClientResponseError as e:
        logger.error(f'HS Deck Helper API is unreachable: {e}')
        await call.answer(CommonMessage.SERVER_UNAVAILABLE)
        return
    except EmptyRequestError as e:
        logger.warning(e)
        await call.answer(CommonMessage.EMPTY_REQUEST_HINT)
        return

    amount = len(cards)
    if amount > MAX_CARDS_IN_RESPONSE:
        await call.answer(CommonMessage.TOO_MANY_RESULTS_HINT_.format(amount))
        return

    cards = list(paginate_list(cards, 9))

    await state.update_data(cardlist={'cards': cards, 'page': 1, 'total': amount})

    data = await state.get_data()
    response = AnswerBuilder(data).cards.result_list()

    try:
        resp_msg = await call.message.reply(text=response.text, reply_markup=response.keyboard)

        # Close keyboard for CardRequestInfoMessage
        await call.message.edit_reply_markup()
    except BadRequest:
        resp_msg = await call.bot.send_message(
            chat_id=call.from_user.id,
            text=response.text,
            reply_markup=response.keyboard,
        )
    await state.update_data(card_response_msg_id=resp_msg.message_id)
    await CardResponse.list.set()
    await call.answer()


def register_card_request_handlers(dp: Dispatcher):
    dp.register_message_handler(card_search_start, commands='cards', state='*')
    dp.register_message_handler(card_search_start, Text(equals='cards', ignore_case=True), state='*')
    dp.register_callback_query_handler(
        card_search_close,
        command_cd.filter(scope='card_request', action='close'),
        state=BuildCardRequest.base,
    )
    dp.register_callback_query_handler(
        card_search_clear,
        command_cd.filter(scope='card_request', action='clear'),
        state=BuildCardRequest.base,
    )
    dp.register_callback_query_handler(
        card_search,
        command_cd.filter(scope='card_request', action='request'),
        state=BuildCardRequest.base,
    )

    dp.register_callback_query_handler(
        card_search_name_input,
        cardparam_cd.filter(param='name', action='add'),
        state=BuildCardRequest.base,
    )
    dp.register_callback_query_handler(
        card_search_type_input,
        cardparam_cd.filter(param='ctype', action='add'),
        state=BuildCardRequest.base,
    )
    dp.register_callback_query_handler(
        card_search_class_input,
        cardparam_cd.filter(param='classes', action='add'),
        state=BuildCardRequest.base,
    )
    dp.register_callback_query_handler(
        card_search_set_input,
        cardparam_cd.filter(param='cset', action='add'),
        state=BuildCardRequest.base,
    )
    dp.register_callback_query_handler(
        card_search_rarity_input,
        cardparam_cd.filter(param='rarity', action='add'),
        state=BuildCardRequest.base,
    )
    dp.register_callback_query_handler(
        card_search_digit_param_input,
        cardparam_cd.filter(param=['cost', 'attack', 'health', 'durability', 'armor'], action='add'),
        state=BuildCardRequest.base,
    )
    dp.register_callback_query_handler(
        card_search_language_input,
        cardparam_cd.filter(param='language', action='add'),
        state=BuildCardRequest.base,
    )
    dp.register_callback_query_handler(
        card_search_collectible_input,
        cardparam_cd.filter(param='coll', action='add'),
        state=BuildCardRequest.base,
    )

    dp.register_callback_query_handler(
        card_search_param_cancel,
        cardparam_cd.filter(action='cancel'),
        state='*',
    )
    dp.register_callback_query_handler(
        card_search_param_clear,
        cardparam_cd.filter(action='clear'),
        state='*',
    )
    dp.register_message_handler(
        card_search_name_entered,
        state=BuildCardRequest.wait_name,
    )
    dp.register_callback_query_handler(
        card_search_type_chosen,
        cardparam_cd.filter(action='submit'),
        state=BuildCardRequest.wait_type,
    )
    dp.register_callback_query_handler(
        card_search_class_chosen,
        cardparam_cd.filter(action='submit'),
        state=BuildCardRequest.wait_class,
    )
    dp.register_callback_query_handler(
        card_search_set_chosen,
        cardparam_cd.filter(action='submit'),
        state=BuildCardRequest.wait_set,
    )
    dp.register_callback_query_handler(
        card_search_rarity_chosen,
        cardparam_cd.filter(action='submit'),
        state=BuildCardRequest.wait_rarity,
    )
    dp.register_message_handler(
        card_search_digit_param_entered,
        state=WaitCardNumericParam.all_states,
    )
