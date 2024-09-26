from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .application import router

import response as response
import keyboards as kb
import states as st
import utils as ut


@router.message(lambda message: message.text == "Дежурства")
async def group_menu(message: Message, state: FSMContext):

    msg = "Выберите пункт из меню"
    keyboard = kb.duty_menu

    await message.answer(msg, reply_markup=keyboard)


@router.message(lambda message: message.text == "Список дежурств")
async def duty_list(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = user_data["token"]

    status, duties = await response.get_duties(token)

    if status == 204:
        await message.answer("Список дежурств пуст", parse_mode="Markdown")

    msg = await ut.create_duties_msg("🧹*Дежурства:*\n\n", duties)
    await message.answer(msg, parse_mode="Markdown")
