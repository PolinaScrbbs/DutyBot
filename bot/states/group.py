from aiogram.fsm.state import StatesGroup, State


class GroupCreate(StatesGroup):
    title = State()


class GroupUpdate(StatesGroup):
    title = State()
