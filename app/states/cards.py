from aiogram.dispatcher.filters.state import State, StatesGroup


class BuildCardRequest(StatesGroup):
    base = State()
    wait_name = State()
    wait_class = State()
    wait_type = State()
    wait_set = State()
    wait_rarity = State()


class WaitCardNumericParam(StatesGroup):
    cost = State()
    attack = State()
    health = State()
    durability = State()
    armor = State()


class CardResponse(StatesGroup):
    list = State()
    detail = State()
