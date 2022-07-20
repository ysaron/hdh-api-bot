import pytest
import asynctest
from unittest.mock import AsyncMock, call, ANY, patch

from app.handlers.card_request import *
from app.handlers.card_response import *
from app.handlers.common import cmd_start, cmd_cancel


class TestCommonHandlers:

    @pytest.mark.asyncio
    async def test_cmd_start(self):
        message_mock = AsyncMock()
        context_mock = AsyncMock()

        with patch('app.services.answer_builders.CommonAnswerBuilder.start') as builder_mock:
            await cmd_start(message=message_mock, state=context_mock)

            context_mock.finish.assert_called_with()
            builder_mock.assert_called_with()
            message_mock.answer.assert_called()

    @pytest.mark.asyncio
    async def test_cmd_cancel(self):
        message_mock = AsyncMock()
        context_mock = AsyncMock()

        with patch('app.services.answer_builders.CommonAnswerBuilder.cancel') as builder_mock:
            await cmd_cancel(message=message_mock, state=context_mock)

            context_mock.finish.assert_called_with()
            builder_mock.assert_called_with()
            message_mock.answer.assert_called()


class TestCardHandlers:

    @pytest.mark.asyncio
    async def test_card_search_start(self, card_request_full_data, remove_keyboard):
        message_mock = AsyncMock()
        context_mock = AsyncMock()
        with asynctest.patch('app.states.cards.BuildCardRequest.base.set') as state_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.request_info') as builder_mock:
            context_mock.get_data.return_value = card_request_full_data
            await card_search_start(message=message_mock, state=context_mock)

            builder_mock.assert_called_with()

            answer_calls = [
                call(text='Starting a new card search...', reply_markup=remove_keyboard),
                call(text=ANY, reply_markup=ANY),
            ]
            message_mock.answer.assert_has_calls(answer_calls)
            state_mock.assert_called()
            context_mock.get_data.assert_called_with()
            context_mock.update_data.assert_called_with(request_msg_id=ANY)

    @pytest.mark.asyncio
    async def test_update_request(self, card_request_full_data):
        test_chat_id = 1
        message_mock = AsyncMock()
        context_mock = AsyncMock()
        context_mock.get_data.return_value = card_request_full_data
        message_mock.chat.id = test_chat_id

        with patch('app.services.answer_builders.CardAnswerBuilder.request_info') as builder_mock:
            await update_request(message=message_mock, state=context_mock, request_data=card_request_full_data)

            builder_mock.assert_called_with()
            context_mock.get_data.assert_called_with()
            message_mock.bot.edit_message_text.assert_called_with(
                ANY,
                chat_id=test_chat_id,
                message_id=card_request_full_data['request_msg_id'],
                reply_markup=ANY,
            )

    @pytest.mark.asyncio
    async def test_card_search_param_cancel(self):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        with asynctest.patch('app.states.cards.BuildCardRequest.base.set') as state_mock:
            await card_search_param_cancel(call=call_mock, state=context_mock)

            call_mock.message.delete.assert_called_with()
            context_mock.update_data.assert_called_with(prompt_msg_id=None)
            state_mock.assert_called_with()

    @pytest.mark.asyncio
    async def test_card_search_param_clear(self, card_request_full_data):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        callback_data = {'param': 'rarity'}
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.states.cards.BuildCardRequest.base.set') as state_mock, \
                asynctest.patch('app.handlers.card_request.update_request') as update_mock:
            await card_search_param_clear(call=call_mock, callback_data=callback_data, state=context_mock)

            call_mock.message.delete.assert_called_with()
            state_mock.assert_called_with()
            context_mock.update_data.assert_called_with({'rarity': None, 'prompt_msg_id': None})
            update_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_card_search_name_input(self, card_request_full_data):
        test_prompt_id = 1
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        prompt_mock = AsyncMock(message_id=test_prompt_id)
        call_mock.message.reply.return_value = prompt_mock
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.states.cards.BuildCardRequest.wait_name.set') as state_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.wait_param') as builder_mock:
            await card_search_name_input(call=call_mock, state=context_mock)

            builder_mock.assert_called_with('name')
            call_mock.message.reply.assert_called_once()
            state_mock.assert_called_with()
            context_mock.update_data.assert_called_with(prompt_msg_id=prompt_mock.message_id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'entered_name',
        [
            'a',
            '123456',
            'Ragnaros the Firelord',
        ]
    )
    async def test_card_search_name_entered_correct(self, card_request_full_data, entered_name):
        message_mock = AsyncMock(text=entered_name)
        context_mock = AsyncMock()
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.states.cards.BuildCardRequest.base.set') as state_mock, \
                asynctest.patch('app.handlers.card_request.clear_prompt') as clear_prompt_mock, \
                asynctest.patch('app.handlers.card_request.update_request') as update_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.invalid_param') as builder_mock:
            await card_search_name_entered(message=message_mock, state=context_mock)

            builder_mock.assert_not_called()
            message_mock.delete.assert_called_with()
            clear_prompt_mock.assert_called_with(message_mock, card_request_full_data, context_mock)
            state_mock.assert_called_with()
            context_mock.update_data.assert_called_with(name=message_mock.text)
            update_mock.assert_called_with(message_mock, context_mock, card_request_full_data)

            message_mock.bot.edit_message_text.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'entered_name',
        [
            'Some text that is too long to be processed as a name',
            'Another text that is also too long to be processed as a name',
            'Yet another texttexttexttexttexttext...',
        ]
    )
    async def test_card_search_name_entered_wrong(self, card_request_full_data, entered_name):
        message_mock = AsyncMock(text=entered_name)
        context_mock = AsyncMock()
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.states.cards.BuildCardRequest.base.set') as state_mock, \
                asynctest.patch('app.handlers.card_request.clear_prompt') as clear_prompt_mock, \
                asynctest.patch('app.handlers.card_request.update_request') as update_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.invalid_param') as builder_mock:
            await card_search_name_entered(message=message_mock, state=context_mock)

            builder_mock.assert_called_with('name')
            message_mock.delete.assert_called_with()
            message_mock.bot.edit_message_text.assert_called_once()

            clear_prompt_mock.assert_not_called()
            state_mock.assert_not_called()
            context_mock.update_data.assert_not_called()
            update_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_card_search_type_input(self, card_request_full_data):
        test_prompt_id = 1
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        prompt_mock = AsyncMock(message_id=test_prompt_id)
        call_mock.message.reply.return_value = prompt_mock
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.states.cards.BuildCardRequest.wait_type.set') as state_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.wait_param') as builder_mock:
            await card_search_type_input(call=call_mock, state=context_mock)

            builder_mock.assert_called_with('ctype')
            call_mock.message.reply.assert_called_once()
            state_mock.assert_called_with()
            context_mock.update_data.assert_called_with(prompt_msg_id=prompt_mock.message_id)
            call_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'type_sign',
        ['M', 'W', 'S', 'H']
    )
    async def test_card_search_type_chosen(self, card_request_full_data, type_sign):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        callback_data = {'param': type_sign}
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.states.cards.BuildCardRequest.base.set') as state_mock, \
                asynctest.patch('app.handlers.card_request.clear_prompt') as clear_prompt_mock, \
                asynctest.patch('app.handlers.card_request.update_request') as update_mock:
            await card_search_type_chosen(call=call_mock, callback_data=callback_data, state=context_mock)

            context_mock.update_data.assert_called()
            clear_prompt_mock.assert_called_with(ANY, card_request_full_data, context_mock)
            state_mock.assert_called_with()
            context_mock.update_data.assert_any_call(ctype=type_sign)
            update_mock.assert_called_with(ANY, context_mock, card_request_full_data)

    @pytest.mark.asyncio
    async def test_card_search_class_input(self, card_request_full_data):
        test_prompt_id = 1
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        prompt_mock = AsyncMock(message_id=test_prompt_id)
        call_mock.message.reply.return_value = prompt_mock
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.states.cards.BuildCardRequest.wait_class.set') as state_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.wait_param') as builder_mock:
            await card_search_class_input(call=call_mock, state=context_mock)

            builder_mock.assert_called_with('classes')
            call_mock.message.reply.assert_called_once()
            state_mock.assert_called_with()
            context_mock.update_data.assert_called_with(prompt_msg_id=prompt_mock.message_id)
            call_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'cls',
        ['Priest', 'Mage', 'Druid'],
    )
    async def test_card_search_class_chosen(self, card_request_full_data, cls):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        callback_data = {'param': cls}
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.states.cards.BuildCardRequest.base.set') as state_mock, \
                asynctest.patch('app.handlers.card_request.clear_prompt') as clear_prompt_mock, \
                asynctest.patch('app.handlers.card_request.update_request') as update_mock:
            await card_search_class_chosen(call=call_mock, callback_data=callback_data, state=context_mock)

            context_mock.update_data.assert_called()
            clear_prompt_mock.assert_called_with(ANY, card_request_full_data, context_mock)
            state_mock.assert_called_with()
            context_mock.update_data.assert_any_call(classes=ANY)
            update_mock.assert_called_with(ANY, context_mock, card_request_full_data)

    @pytest.mark.asyncio
    async def test_card_search_set_input(self, card_request_full_data):
        test_prompt_id = 1
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        prompt_mock = AsyncMock(message_id=test_prompt_id)
        call_mock.message.reply.return_value = prompt_mock
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.states.cards.BuildCardRequest.wait_set.set') as state_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.wait_param') as builder_mock:
            await card_search_set_input(call=call_mock, state=context_mock)

            builder_mock.assert_called_with('cset')
            call_mock.message.reply.assert_called_once()
            state_mock.assert_called_with()
            context_mock.update_data.assert_called_with(prompt_msg_id=prompt_mock.message_id)
            call_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'cset',
        [
            'United in Stormwind',
            'Naxxramas',
            'Madness At The Darkmoon Faire',
        ]
    )
    async def test_card_search_set_chosen(self, card_request_full_data, cset):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        callback_data = {'param': cset}
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.states.cards.BuildCardRequest.base.set') as state_mock, \
                asynctest.patch('app.handlers.card_request.clear_prompt') as clear_prompt_mock, \
                asynctest.patch('app.handlers.card_request.update_request') as update_mock:
            await card_search_set_chosen(call=call_mock, callback_data=callback_data, state=context_mock)

            context_mock.update_data.assert_called()
            clear_prompt_mock.assert_called_with(ANY, card_request_full_data, context_mock)
            state_mock.assert_called_with()
            context_mock.update_data.assert_any_call(cset=cset)
            update_mock.assert_called_with(ANY, context_mock, card_request_full_data)

    @pytest.mark.asyncio
    async def test_card_search_rarity_input(self, card_request_full_data):
        test_prompt_id = 1
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        prompt_mock = AsyncMock(message_id=test_prompt_id)
        call_mock.message.reply.return_value = prompt_mock
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.states.cards.BuildCardRequest.wait_rarity.set') as state_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.wait_param') as builder_mock:
            await card_search_rarity_input(call=call_mock, state=context_mock)

            builder_mock.assert_called_with('rarity')
            call_mock.message.reply.assert_called_once()
            state_mock.assert_called_with()
            context_mock.update_data.assert_called_with(prompt_msg_id=prompt_mock.message_id)
            call_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'rarity_sign',
        ['L', 'E', 'R', 'C', 'NO']
    )
    async def test_card_search_rarity_chosen(self, card_request_full_data, rarity_sign):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        callback_data = {'param': rarity_sign}
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.states.cards.BuildCardRequest.base.set') as state_mock, \
                asynctest.patch('app.handlers.card_request.clear_prompt') as clear_prompt_mock, \
                asynctest.patch('app.handlers.card_request.update_request') as update_mock:
            await card_search_rarity_chosen(call=call_mock, callback_data=callback_data, state=context_mock)

            context_mock.update_data.assert_called()
            clear_prompt_mock.assert_called_with(ANY, card_request_full_data, context_mock)
            state_mock.assert_called_with()
            context_mock.update_data.assert_any_call(rarity=rarity_sign)
            update_mock.assert_called_with(ANY, context_mock, card_request_full_data)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'param',
        ['cost', 'attack', 'health', 'durability', 'armor']
    )
    async def test_card_search_digit_param_input(self, card_request_full_data, param):
        test_prompt_id = 1
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        prompt_mock = AsyncMock(message_id=test_prompt_id)
        callback_data = {'param': param}
        call_mock.message.reply.return_value = prompt_mock
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch(f'app.states.cards.WaitCardNumericParam.{param}.set') as state_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.wait_param') as builder_mock:
            await card_search_digit_param_input(call=call_mock, callback_data=callback_data, state=context_mock)

            builder_mock.assert_called_with(param)
            call_mock.message.reply.assert_called_once()
            state_mock.assert_called_with()
            context_mock.update_data.assert_called_with(prompt_msg_id=prompt_mock.message_id)
            call_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'param,value',
        [
            ('5', 'cost'),
            ('0', 'attack'),
            ('29', 'health'),
            ('1', 'durability'),
            ('10', 'armor'),
        ]
    )
    async def test_card_search_digit_param_entered_correct(self, card_request_full_data, param, value):
        message_mock = AsyncMock(text=param)
        context_mock = AsyncMock()
        context_mock.get_data.return_value = card_request_full_data
        context_mock.get_state.return_value = f'insignificant:{param}'

        with asynctest.patch('app.states.cards.BuildCardRequest.base.set') as state_mock, \
                asynctest.patch('app.handlers.card_request.clear_prompt') as clear_prompt_mock, \
                asynctest.patch('app.handlers.card_request.update_request') as update_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.invalid_param') as builder_mock:
            await card_search_digit_param_entered(message=message_mock, state=context_mock)

            message_mock.delete.assert_called_with()
            clear_prompt_mock.assert_called_with(message_mock, card_request_full_data, context_mock)
            state_mock.assert_called_with()
            context_mock.update_data.assert_called_with({param: message_mock.text})
            update_mock.assert_called_with(message_mock, context_mock, card_request_full_data)

            builder_mock.assert_not_called()
            message_mock.bot.edit_message_text.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'param,value',
        [
            ('string', 'cost'),
            ('-1', 'attack'),
            ('2.5', 'health'),
            ('-10', 'durability'),
            ('AAA', 'armor'),
        ]
    )
    async def test_card_search_digit_param_entered_wrong(self, card_request_full_data, param, value):
        message_mock = AsyncMock(text=param)
        context_mock = AsyncMock()
        context_mock.get_data.return_value = card_request_full_data
        context_mock.get_state.return_value = f'insignificant:{param}'

        with asynctest.patch('app.states.cards.BuildCardRequest.base.set') as state_mock, \
                asynctest.patch('app.handlers.card_request.clear_prompt') as clear_prompt_mock, \
                asynctest.patch('app.handlers.card_request.update_request') as update_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.invalid_param') as builder_mock:
            await card_search_digit_param_entered(message=message_mock, state=context_mock)

            clear_prompt_mock.assert_not_called()
            state_mock.assert_not_called()
            context_mock.update_data.assert_not_called()
            update_mock.assert_not_called()

            message_mock.delete.assert_called_with()
            builder_mock.assert_called_with(param)
            message_mock.bot.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_card_search_close(self, card_request_full_data):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.handlers.card_request.clear_all') as clear_all_mock, \
                patch('app.services.answer_builders.CommonAnswerBuilder.cancel') as builder_mock:
            await card_search_close(call=call_mock, state=context_mock)

            clear_all_mock.assert_called_once()
            builder_mock.assert_called_with()
            call_mock.bot.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_card_search_clear(self, card_request_full_data):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        context_mock.get_data.return_value = card_request_full_data

        with asynctest.patch('app.handlers.card_request.update_request') as update_mock:
            await card_search_clear(call=call_mock, state=context_mock)

            context_mock.update_data.assert_called_once()
            update_mock.assert_called_with(ANY, context_mock, card_request_full_data)
            call_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_card_search(self, card_request_full_data, card_list_full_data):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        context_mock.get_data.return_value = card_request_full_data | card_list_full_data

        with asynctest.patch('app.handlers.card_request.RequestCards.perform') as api_mock, \
                patch('app.states.cards.CardResponse.list.set') as state_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.result_list') as builder_mock:
            api_mock.return_value = card_list_full_data['cardlist']['cards']
            await card_search(call=call_mock, state=context_mock)

            api_mock.assert_called_with()
            context_mock.update_data.assert_any_call(cardlist=ANY)
            builder_mock.assert_called_with()
            call_mock.message.reply.assert_called_once()
            context_mock.update_data.assert_any_call(response_msg_id=ANY)
            state_mock.assert_called_with()
            call_mock.answer.assert_called_once()

    # -----------------------------------------------------------------------------------------

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'direction',
        ['left', 'right']
    )
    async def test_card_list_pages_flip(self, card_list_full_data, direction):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        context_mock.get_data.return_value = card_list_full_data
        callback_data = {'action': direction}

        with patch('app.services.answer_builders.CardAnswerBuilder.result_list') as builder_mock:
            await card_list_pages(call=call_mock, callback_data=callback_data, state=context_mock)

            context_mock.update_data.assert_called_with(cardlist=ANY)
            builder_mock.assert_called_with()
            call_mock.bot.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_card_list_pages_pages_btn(self):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        callback_data = {'action': 'pages'}

        await card_list_pages(call=call_mock, callback_data=callback_data, state=context_mock)

        call_mock.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_card_list_pages_close(self, card_list_full_data):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        callback_data = {'action': 'close'}

        with patch('app.states.cards.BuildCardRequest.base.set') as state_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.request_info') as builder_mock:
            await card_list_pages(call=call_mock, callback_data=callback_data, state=context_mock)

            call_mock.message.delete.assert_called_with()
            state_mock.assert_called_with()
            builder_mock.assert_called_with()
            call_mock.bot.edit_message_reply_markup.assert_called_once()
            context_mock.update_data.assert_called_with(response_msg_id=None, cardlist=None, card_detail=None)

    @pytest.mark.asyncio
    async def test_card_list_pages_unknown(self):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        callback_data = {'action': 'unknown_action'}

        with pytest.raises(ValueError):
            await card_list_pages(call=call_mock, callback_data=callback_data, state=context_mock)

    @pytest.mark.asyncio
    async def test_card_list_get_card(self, card_detail_full_data):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        context_mock.get_data.return_value = card_detail_full_data
        callback_data = {'id': 49184}

        with asynctest.patch('app.handlers.card_response.RequestSingleCard.perform') as api_mock, \
                patch('app.services.answer_builders.CardAnswerBuilder.result_detail') as builder_mock:
            api_mock.return_value = card_detail_full_data['card_detail']
            await card_list_get_card(call=call_mock, callback_data=callback_data, state=context_mock)

            api_mock.assert_called_with()
            context_mock.update_data.assert_called_with(card_detail=card_detail_full_data['card_detail'])
            builder_mock.assert_called_with()
            call_mock.bot.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_card_detail_back_to_list(self, card_detail_full_data):
        call_mock = AsyncMock()
        context_mock = AsyncMock()
        context_mock.get_data.return_value = card_detail_full_data

        with patch('app.services.answer_builders.CardAnswerBuilder.result_list') as builder_mock:
            await card_detail_back_to_list(call=call_mock, state=context_mock)

            builder_mock.assert_called_with()
            call_mock.bot.edit_message_text.assert_called_once()