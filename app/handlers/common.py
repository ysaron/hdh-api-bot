from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from app.services.utils import clear_all
from app.services.answer_builders import AnswerBuilder


async def cmd_start(message: types.Message, state: FSMContext):
    """ Main menu """
    await state.finish()
    response = AnswerBuilder({}).common.start()
    await message.answer(text=response.text, reply_markup=response.keyboard)


async def cmd_cancel(message: types.Message, state: FSMContext):
    """ Delete all stored messages and return to main menu """
    await clear_all(message, state)
    response = AnswerBuilder({}).common.cancel()
    await message.answer(text=response.text, reply_markup=response.keyboard)


def register_common_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start', state='*')
    dp.register_message_handler(cmd_cancel, commands='cancel', state='*')
