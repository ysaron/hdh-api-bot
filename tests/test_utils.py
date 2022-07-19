import pytest

from app.services import utils


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
