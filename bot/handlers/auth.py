from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .special import router

import keyboards as kb
import states as st
import utils as ut
import response as response


@router.message(lambda message: message.text == "Регистрация")
async def get_full_name(message: Message, state: FSMContext):
    await state.set_state(st.Registration.full_name)
    await message.answer("👨‍🎓Введите ФИО", reply_markup=kb.cancel)


@router.message(st.Registration.full_name)
async def get_password(message: Message, state: FSMContext):
    await state.update_data({message.from_user.id: {"full_name": message.text}})

    await state.set_state(st.Registration.password)
    await message.answer("🔑Создайте пароль", reply_markup=kb.cancel)


@router.message(st.Registration.password)
async def get_confirm_password(message: Message, state: FSMContext):
    user_data = await ut.get_user_data(state, message.from_user.id)
    user_data["password"] = message.text
    await state.update_data({message.from_user.id: user_data})

    await state.set_state(st.Registration.confirm_password)
    await message.answer("🔑Подтвердите пароль ", reply_markup=kb.cancel)


@router.message(st.Registration.confirm_password)
async def registration(message: Message, state: FSMContext):
    user_data = await ut.get_user_data(state, message.from_user.id)

    username = message.from_user.username
    password = user_data.get("password", None)
    confirm_password = message.text
    full_name = user_data.get("full_name", None)

    status, json_response = await response.registraion(
        username, password, confirm_password, full_name
    )

    if status == 201:
        await message.answer(json_response["message"])

    await message.answer(f"❌ *{json_response['detail'].upper()}* ", "Markdown")
