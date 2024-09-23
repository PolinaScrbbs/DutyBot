from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    full_name = State()
    password = State()
    confirm_password = State()


class Authorization(StatesGroup):
    login = State()
    password = State()
