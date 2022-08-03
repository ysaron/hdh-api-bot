import pytest


@pytest.mark.parametrize(
    'buttons,cols,expected',
    [
        (['btn1', 'btn2', 'btn3'], 2, [('btn1', 'btn2'), 'btn3']),
        (['btn1', 'btn2', 'btn3'], 3, [('btn1', 'btn2', 'btn3')]),
        (['btn1', 'btn2', 'btn3', 'btn4'], 2, [('btn1', 'btn2'), ('btn3', 'btn4')]),
        (['btn1', 'btn2', 'btn3', 'btn4', 'btn5', 'btn6'], 5, [('btn1', 'btn2', 'btn3', 'btn4', 'btn5'), 'btn6']),
    ]
)
def test_group_buttons(common_keyboard_builder_obj, buttons, cols, expected):
    assert common_keyboard_builder_obj.group_buttons(buttons, cols) == expected


def test_fill(common_keyboard_builder_obj, reply_keyboard):
    btns = [('btn1', 'btn2', 'btn3', 'btn4', 'btn5'), 'btn6']
    invalid_btns = [['btn1', 'btn2', 'btn3', 'btn4', 'btn5'], 'btn6']
    with pytest.raises(AttributeError):
        common_keyboard_builder_obj.fill(btns)

    common_keyboard_builder_obj.keyboard = reply_keyboard

    with pytest.raises(ValueError):
        common_keyboard_builder_obj.fill(invalid_btns)

    common_keyboard_builder_obj.fill(btns)
    assert common_keyboard_builder_obj.keyboard.keyboard == [['btn1', 'btn2', 'btn3'], ['btn4', 'btn5'], ['btn6']]


class TestCommonKeyboardBuilder:

    def test_common_keyboard_builder_default(self, common_keyboard_builder_obj, reply_keyboard):
        common_keyboard_builder_obj.keyboard = reply_keyboard
        assert common_keyboard_builder_obj.default().keyboard == [['Cards', 'Decks'], ['Decode Deckstring']]


class TestCardKeyboardBuilder:

    def test_card_keyboard_builder_request_info(self, card_request_keyboard_builder_obj, inline_keyboard):
        card_request_keyboard_builder_obj.keyboard = inline_keyboard
        kb = card_request_keyboard_builder_obj.request_info().inline_keyboard
        assert isinstance(kb, list)
        assert all(isinstance(row, list) for row in kb)
        assert len(kb[-1]) == 3, 'last row must include 3 buttons'
        request_btn, clear_btn, close_btn = kb[-1]

        invalid_last_row = 'last row must consist of 3 buttons: REQUEST, CLEAR, CLOSE'
        assert request_btn.text == 'REQUEST', invalid_last_row
        assert clear_btn.text == 'CLEAR', invalid_last_row
        assert close_btn.text == 'CLOSE', invalid_last_row

    def test_card_keyboard_builder_wait_param(self, card_request_keyboard_builder_obj, inline_keyboard):
        card_request_keyboard_builder_obj.keyboard = inline_keyboard

        # for parameter saved in request context
        kb = card_request_keyboard_builder_obj.wait_param('rarity').inline_keyboard
        assert isinstance(kb, list)
        assert all(isinstance(row, list) for row in kb)
        assert len(kb[-1]) == 2, 'last row of the keyboard for saved parameter must include 2 buttons'
        cancel_btn, clear_btn = kb[-1]
        invalid_last_row = 'last row must consist of 2 buttons: CANCEL, CLEAR'
        assert cancel_btn.text == 'CANCEL', invalid_last_row
        assert clear_btn.text == 'CLEAR', invalid_last_row

        # for parameter NOT saved in request context
        kb = card_request_keyboard_builder_obj.wait_param('armor').inline_keyboard
        assert isinstance(kb, list)
        assert all(isinstance(row, list) for row in kb)
        assert len(kb[-1]) == 1, 'last row of the keyboard for parameter=None must include 1 button'
        cancel_btn = kb[-1][0]
        assert cancel_btn.text == 'CANCEL', 'last row must consist of 1 button: CANCEL'

    def test_card_keyboard_builder_result_list(self, card_list_keyboard_builder_obj, inline_keyboard):
        card_list_keyboard_builder_obj.keyboard = inline_keyboard
        kb = card_list_keyboard_builder_obj.result_list().inline_keyboard
        assert isinstance(kb, list)
        assert all(isinstance(row, list) for row in kb)

        last_row_msg = 'last row must consist of 1 button: CLOSE'
        assert len(kb[-1]) == 1, last_row_msg
        assert kb[-1][0].text == 'CLOSE', last_row_msg

        penultimate_row_msg = 'penultimate row must consist of 3 buttons: left, page info, right'
        assert len(kb[-2]) == 3, penultimate_row_msg
        left, info, right = kb[-2]
        assert left.callback_data == 'cmd:card_pages:left:', penultimate_row_msg
        assert info.callback_data == 'cmd:card_pages:pages:', penultimate_row_msg
        assert right.callback_data == 'cmd:card_pages:right:', penultimate_row_msg

    def test_card_keyboard_builder_result_detail(self, card_detail_keyboard_builder_obj, inline_keyboard):
        card_detail_keyboard_builder_obj.keyboard = inline_keyboard
        kb = card_detail_keyboard_builder_obj.result_detail().inline_keyboard

        assert isinstance(kb, list)
        assert all(isinstance(row, list) for row in kb)
        last_row_msg = 'last row must consist of 2 buttons: BACK, CLOSE'
        assert len(kb[-1]) == 2, last_row_msg
        back, close = kb[-1]
        assert back.text == 'BACK', last_row_msg
        assert close.text == 'CLOSE', last_row_msg


class TestDeckKeyboardBuilder:

    def test_deck_keyboard_builder_request_info(self, deck_request_keyboard_builder_obj, inline_keyboard):
        deck_request_keyboard_builder_obj.keyboard = inline_keyboard
        kb = deck_request_keyboard_builder_obj.request_info().inline_keyboard
        assert isinstance(kb, list)
        assert all(isinstance(row, list) for row in kb)
        assert len(kb[-1]) == 3, 'last row must include 3 buttons'
        request_btn, clear_btn, close_btn = kb[-1]

        invalid_last_row = 'last row must consist of 3 buttons: REQUEST, CLEAR, CLOSE'
        assert request_btn.text == 'REQUEST', invalid_last_row
        assert clear_btn.text == 'CLEAR', invalid_last_row
        assert close_btn.text == 'CLOSE', invalid_last_row

    def test_deck_keyboard_builder_wait_param(self, deck_request_keyboard_builder_obj, inline_keyboard):
        deck_request_keyboard_builder_obj.keyboard = inline_keyboard

        # for parameter saved in request context
        kb = deck_request_keyboard_builder_obj.wait_param('dformat').inline_keyboard
        assert isinstance(kb, list)
        assert all(isinstance(row, list) for row in kb)
        assert len(kb[-1]) == 2, 'last row of the keyboard for saved parameter must include 2 buttons'
        cancel_btn, clear_btn = kb[-1]
        invalid_last_row = 'last row must consist of 2 buttons: CANCEL, CLEAR'
        assert cancel_btn.text == 'CANCEL', invalid_last_row
        assert clear_btn.text == 'CLEAR', invalid_last_row

    def test_deck_keyboard_builder_result_list(self, deck_list_keyboard_builder_obj, inline_keyboard):
        deck_list_keyboard_builder_obj.keyboard = inline_keyboard
        kb = deck_list_keyboard_builder_obj.result_list().inline_keyboard
        assert isinstance(kb, list)
        assert all(isinstance(row, list) for row in kb)

        last_row_msg = 'last row must consist of 1 button: CLOSE'
        assert len(kb[-1]) == 1, last_row_msg
        assert kb[-1][0].text == 'CLOSE', last_row_msg

        penultimate_row_msg = 'penultimate row must consist of 3 buttons: left, page info, right'
        assert len(kb[-2]) == 3, penultimate_row_msg
        left, info, right = kb[-2]
        assert left.callback_data == 'cmd:deck_pages:left:', penultimate_row_msg
        assert info.callback_data == 'cmd:deck_pages:pages:', penultimate_row_msg
        assert right.callback_data == 'cmd:deck_pages:right:', penultimate_row_msg

    def test_deck_keyboard_builder_result_detail(self, deck_detail_keyboard_builder_obj, inline_keyboard):
        deck_detail_keyboard_builder_obj.keyboard = inline_keyboard
        kb = deck_detail_keyboard_builder_obj.result_detail().inline_keyboard

        assert isinstance(kb, list)
        assert all(isinstance(row, list) for row in kb)
        last_row_msg = 'last row must consist of 2 buttons: BACK, CLOSE'
        assert len(kb[-1]) == 2, last_row_msg
        back, close = kb[-1]
        assert back.text == 'BACK', last_row_msg
        assert close.text == 'CLOSE', last_row_msg
