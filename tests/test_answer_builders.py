from aiogram.types import InlineKeyboardMarkup

from app.services.answer_builders import AnswerBuilder, BotAnswer
from app.services.messages import CommonMessage


class TestCommonAnswerBuilder:

    def test_common_answer_builder_start(self):
        answer = AnswerBuilder({}).common.start()
        assert isinstance(answer, BotAnswer)
        assert answer.text == CommonMessage.START
        assert answer.keyboard.keyboard == [['Cards', 'Decks'], ['Decode Deckstring']]

    def test_common_answer_builder_cancel(self):
        answer = AnswerBuilder({}).common.cancel()
        assert isinstance(answer, BotAnswer)
        assert answer.text == CommonMessage.CANCEL
        assert answer.keyboard.keyboard == [['Cards', 'Decks'], ['Decode Deckstring']]


class TestCardAnswerBuilder:

    def test_card_answer_builder_request_info(self, card_request_data):
        answer = AnswerBuilder(card_request_data).cards.request_info()
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)

    def test_card_answer_builder_wait_param(self, card_request_data):
        answer = AnswerBuilder(card_request_data).cards.wait_param('rarity')
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)

        answer = AnswerBuilder(card_request_data).cards.wait_param('armor')
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)

    def test_card_answer_builder_invalid_param(self, card_request_data):
        answer = AnswerBuilder(card_request_data).cards.invalid_param('rarity')
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)

        answer = AnswerBuilder(card_request_data).cards.invalid_param('armor')
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)

    def test_card_answer_builder_result_list(self, card_list_data):
        answer = AnswerBuilder(card_list_data).cards.result_list()
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)

    def test_card_answer_builder_result_detail(self, card_detail_data):
        answer = AnswerBuilder(card_detail_data).cards.result_detail()
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)


class TestDeckAnswerBuilder:

    def test_deck_answer_builder_decode_prompt(self):
        answer = AnswerBuilder({}).decks.decode_prompt()
        assert isinstance(answer, BotAnswer)
        assert answer.text == CommonMessage.DECODE_DECK_PROMPT
        assert answer.keyboard is None

    def test_deck_answer_builder_deck_detail(self, deck_detail_full_data):
        answer = AnswerBuilder(deck_detail_full_data).decks.deck_detail()
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert answer.keyboard is None

    def test_deck_answer_builder_request_info(self, deck_request_data):
        answer = AnswerBuilder(deck_request_data).decks.request_info()
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)

    def test_deck_answer_builder_wait_param(self, deck_request_data):
        answer = AnswerBuilder(deck_request_data).decks.wait_param('dformat')
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)

        answer = AnswerBuilder(deck_request_data).decks.wait_param('dclass')
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)

    def test_deck_answer_builder_invalid_param(self, deck_request_data):
        answer = AnswerBuilder(deck_request_data).decks.invalid_param('dformat')
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)

        answer = AnswerBuilder(deck_request_data).decks.invalid_param('dclass')
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)

    def test_deck_answer_builder_result_list(self, deck_list_full_data):
        answer = AnswerBuilder(deck_list_full_data).decks.result_list()
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)

    def test_deck_answer_builder_result_detail(self, deck_detail_full_data):
        answer = AnswerBuilder(deck_detail_full_data).decks.result_detail()
        assert isinstance(answer, BotAnswer)
        assert isinstance(answer.text, str)
        assert isinstance(answer.keyboard, InlineKeyboardMarkup)
