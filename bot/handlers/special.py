from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import keyboards as kb
import response as response
import utils as ut

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await ut.get_user_data(state, user_id)
    token = user_data.get("token", None)

    if token:
        msg = (
            f"С возвращением, @{message.from_user.username}👋 \nВыбери пункт из меню🔍"
        )
        keyboard = kb.ungroup_main
    else:
        msg = "Привет👋\nВыбери пункт из меню🔍"
        keyboard = kb.start

    await message.answer(text=msg, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data == "cancel")
async def catalog(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("✅ Отменено")


@router.callback_query(F.data == "close")
async def catalog(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("✅ Закрыто")
