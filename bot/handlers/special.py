from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import response as response
import keyboards as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = user_data.get("token", None)

    if token:
        msg = (
            f"С возвращением, @{message.from_user.username}👋 \nВыбери пункт из меню🔍"
        )

        status, user = await response.get_user_by_username(
            message.from_user.username, token
        )
        user_data["user"] = user
        await state.update_data(user_data)

        if user["role"] == "Админ":
            pass
        elif user["group_id"] is not None:
            group = await response.get_group(token)
            user_data["group"] = group
            await state.update_data(user_data)

            if user["role"] == "Студент":
                pass
            elif user["role"] == "Староста":
                keyboard = kb.elder_main
        else:
            keyboard = kb.ungroup_main

    else:
        msg = "Привет👋\nВыбери пункт из меню🔍"
        keyboard = kb.start

    await message.answer(text=msg, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = user_data["token"]
    user = user_data["user"]
    group = user_data["group"]

    await state.clear()
    await state.update_data({"token": token, "user": user, "group": group})

    await callback.message.edit_text("✅ Отменено")


@router.callback_query(F.data == "close")
async def close(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = user_data["token"]
    user = user_data["user"]
    group = user_data["group"]

    await state.clear()
    await state.update_data({"token": token, "user": user, "group": group})

    await callback.message.edit_text("✅ Закрыто")
