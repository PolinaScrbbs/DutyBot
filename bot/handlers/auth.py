from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .special import router, cmd_start

import response as response
import keyboards as kb
import states as st
import utils as ut


@router.message(lambda message: message.text == "Регистрация")
async def get_full_name(message: Message, state: FSMContext):
    await state.set_state(st.Registration.full_name)
    await message.answer("👨‍🎓Введите ФИО", reply_markup=kb.cancel)


@router.message(st.Registration.full_name)
async def get_password(message: Message, state: FSMContext):
    await state.update_data({"full_name": message.text})

    await state.set_state(st.Registration.password)
    await message.answer("🔑Создайте пароль", reply_markup=kb.cancel)


@router.message(st.Registration.password)
async def get_confirm_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_data["password"] = message.text
    await state.update_data(user_data)

    await state.set_state(st.Registration.confirm_password)
    await message.answer("🔑Подтвердите пароль ", reply_markup=kb.cancel)


@router.message(st.Registration.confirm_password)
async def registration(message: Message, state: FSMContext):
    user_data = await state.get_data()

    username = message.from_user.username
    password = str(user_data["password"])
    confirm_password = str(message.text)
    full_name = str(user_data["full_name"])

    status, json_response = await response.registraion(
        username, password, confirm_password, full_name
    )

    await state.clear()
    if status == 201:
        await message.answer(f"*{json_response['message'].upper()}*", "Markdown")
    else:
        await message.answer(f"❌ *{json_response['detail'].upper()}*", "Markdown")


@router.message(lambda message: message.text == "Авторизация")
async def get_password(message: Message, state: FSMContext):
    await state.set_state(st.Authorization.password)
    await message.answer("🔑Введите пароль", reply_markup=kb.cancel)


@router.message(st.Authorization.password)
async def authorazation(message: Message, state: FSMContext):
    username = message.from_user.username
    password = str(message.text)

    status, json_response = await response.authorization(username, password)

    await state.clear()
    if status in [200, 201]:
        await state.update_data({"token": json_response["token"]})
        await message.answer(
            f"✅ *{json_response['message'].upper()}*",
            "Markdown",
        )

        await cmd_start(message, state)
    else:
        await message.answer(
            f"❌ *{json_response['detail'].upper()}*", "Markdown", reply_markup=kb.start
        )
