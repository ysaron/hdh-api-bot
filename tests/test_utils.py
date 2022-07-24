import pytest
import asynctest
from unittest.mock import AsyncMock, patch

from app.services import utils
from app.exceptions import DeckstringError


@pytest.mark.parametrize(
    'string,expected',
    [
        ('string', False),
        ('2.5', False),
        ('-1', False),
        ('5', True),
        ('0', True),
    ]
)
def test_is_positive_integer(string, expected):
    assert utils.is_positive_integer(string) == expected


@pytest.mark.parametrize(
    'lst,n,expected',
    [
        ([i for i in range(1, 14)], 5, [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13]]),
        ([i * i for i in range(5, 18, 3)], 3, [[25, 64, 121], [196, 289]]),
        ([5, 5, 5], 2, [[5, 5], [5]]),
        ([5, 4, 3, 2], 4, [[5, 4, 3, 2]]),
        ([5, 4, 3, 2], 2, [[5, 4], [3, 2]]),
    ]
)
def test_paginate_list(lst, n, expected):
    assert list(utils.paginate_list(lst, n)) == expected


@pytest.mark.parametrize(
    'direction,current,npages,expected',
    [
        ('right', 3, 5, 4),
        ('left', 3, 5, 2),
        ('right', 5, 5, 1),
        ('left', 1, 5, 5),
        ('right', 6, 7, 7),
        ('left', 2, 10, 1),
    ]
)
def test_flip_page(direction, current, npages, expected):
    with pytest.raises(ValueError):
        utils.flip_page(direction='up', current_page=1, npages=2)

    assert utils.flip_page(direction, current, npages) == expected


def test_extract_deckstring(decklist_from_game, pure_deckstring):
    assert utils.extract_deckstring(decklist_from_game) == pure_deckstring
    with pytest.raises(DeckstringError):
        utils.extract_deckstring('asdf # asdf')


@pytest.mark.parametrize(
    'deckstring',
    [
        'AAECAaIHBqH5A/uKBMeyBNi2BNu5BIukBQyq6wP+7gO9gAT3nwS6pAT7pQTspwT5rAS3swSZtgTVtgT58QQA',
        'AAEBAf0GKPoO9Q/YuwLzvQLfxAKQxwLnywKuzQKgzgLy0AKc+ALUhgPiiQOAigPamwP8owPrrAOVzQPXzgPO4QP'
        '44wOS5AOT5AOm7wPQ+QOB+wOC+wOD+wOwkQSDoATnoATHsgT1xwT1zgSW1ASY1ASa1ASX7wSyngWFoAQAAA==',
        'AAECAa0GBNTtA4f3A+iLBImyBA2Z6wPT+QOMgQStigSFnwTLoASEowSKowSitgSktgT00wSh1AT28QQA',
        'AAECAZICAA+t7AOz7APJ9QPs9QP09gOB9wOE9wOsgASvgATnpASXpQS4vgSuwASozgSB1AQA',
    ]
)
def test_is_valid_deckstring_yes(deckstring):
    assert utils.is_valid_deckstring(deckstring)


@pytest.mark.parametrize(
    'deckstring',
    [
        'AAECAaIHBqH5A/uKBMeyBNi2BNu5BIuk-BQyq6wP+7gO9gAT3nwS6pAT7pQTspwT5rAS3swSZtgTVtgT58QQA',
        'AAEBAf0GKPoO9Q/YuwLzvQLfxAKQxwLnywKuzQKgzgLy0AKc+ALUhgPiiQOA_igPamwP8owPrrAOVzQPXzgPO4QP'
        '44wOS5AOT5AOm7wPQ+QOB+wOC+wOD+wOwkQSDoATnoATHsgT1xwT1zgSW1ASY1ASa1ASX7wSyngWFoAQAAA==',
        'QQECAa0GBNTtA4f3A+iLBImyBA2Z6wPT+QOMgQStigSFnwTLoASEowSKowSitgSktgT00wSh1AT28QQA',
        'string',
    ]
)
def test_is_valid_deckstring_no(deckstring):
    assert not utils.is_valid_deckstring(deckstring)


@pytest.mark.asyncio
async def test_deck_decode(pure_deckstring, deck_detail_data):
    message_mock = AsyncMock()
    context_mock = AsyncMock()
    context_mock.get_data.return_value = deck_detail_data

    with asynctest.patch('app.services.utils.RequestDecodeDeck.post') as api_mock, \
            patch('app.services.answer_builders.DeckAnswerBuilder.deck_detail') as builder_mock:
        api_mock.return_value = deck_detail_data
        await utils.deck_decode(message=message_mock, state=context_mock, deckstring=pure_deckstring)

        api_mock.assert_called_with({'d': pure_deckstring})
        context_mock.update_data.assert_called_with(deck=deck_detail_data)
        builder_mock.assert_called_with()
        message_mock.reply.assert_called()
