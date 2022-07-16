from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound

from contextlib import suppress


def is_positive_integer(string: str) -> bool:
    """
    Doctest-style for clarity:

    >>> is_positive_integer('string')
    False
    >>> is_positive_integer('2.5')
    False
    >>> is_positive_integer('-1')
    False
    >>> is_positive_integer('5')
    True
    >>> is_positive_integer('0')
    True
    """
    if not string.isdigit():
        return False
    if int(string) < 0:
        return False
    return True


def paginate_list(lst: list, n: int):
    """ Split list into n sublists """
    for x in range(0, len(lst), n):
        page = lst[x:n + x]
        yield page


def flip_page(direction: str, current_page: int, npages: int) -> int:
    """
    :param direction: "left" or "right"
    :param current_page: page number before flipping
    :param npages: total number of pages
    :return: new page number
    :raise ValueError: if direction is unsupported
    """

    match direction:
        case 'left':
            return current_page - 1 if current_page > 1 else npages
        case 'right':
            return current_page + 1 if current_page < npages else 1
        case _:
            raise ValueError(f'Unknown page flipping direction: {direction}')


async def clear_all(message: types.Message, state: FSMContext):
    """ Delete all stored messages """
    data = await state.get_data()
    for key in ['request_msg_id', 'prompt_msg_id', 'response_msg_id']:
        if data.get(key):
            with suppress(MessageToDeleteNotFound):
                await message.bot.delete_message(chat_id=message.chat.id, message_id=data[key])
    await state.finish()


async def clear_prompt(message: types.Message, data: dict, state: FSMContext):
    """ Delete message for request parameter clarification, then forget it """
    if data.get('prompt_msg_id'):
        with suppress(MessageToDeleteNotFound):
            await message.bot.delete_message(message.chat.id, data['prompt_msg_id'])
        await state.update_data(prompt_msg_id=None)
