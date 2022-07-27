from aiogram.dispatcher.filters.state import State, StatesGroup


class BuildDeckRequest(StatesGroup):
    base = State()
    wait_format = State()
    wait_class = State()
    wait_date = State()


class DeckResponse(StatesGroup):
    list = State()
    detail = State()
