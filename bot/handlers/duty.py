from shutil import ExecError
from uu import Error
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .application import router

import response as response
import keyboards as kb
import utils as ut


@router.message(lambda message: message.text == "Дежурства")
async def group_menu(message: Message):

    msg = "Выберите пункт из меню"
    keyboard = kb.duty_menu

    await message.answer(msg, reply_markup=keyboard)


@router.message(lambda message: message.text == "Назначить дежурных")
async def get_attendant(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = user_data["token"]
    missed_students_id = user_data.get("missed_students_id", None)

    if not missed_students_id:
        missed_students_id = []
        user_data["missed_students_id"] = missed_students_id

    status, attendants = await response.get_attendants(token, missed_students_id)

    user_data["attendants_id"] = [attendants[0]["id"], attendants[1]["id"]]
    await state.update_data(user_data)

    if status == 200:
        try:
            try:
                await message.edit_text(
                    f"👷🏿*{attendants[0]['full_name']}* 👷🏿*{attendants[1]['full_name']}*",
                    reply_markup=kb.remap,
                    parse_mode="Markdown",
                )
            except Exception:
                await message.answer(
                    f"👷🏿*{attendants[0]['full_name']}* 👷🏿*{attendants[1]['full_name']}*",
                    reply_markup=kb.remap,
                    parse_mode="Markdown",
                )
        except Exception:
            await message.edit_text(
                "❗Куда гонишь?", reply_markup=kb.remap, parse_mode="Markdown"
            )


@router.callback_query(lambda query: query.data.startswith("remap_"))
async def remap(callback: CallbackQuery, state: FSMContext):
    remap_num = int(callback.data.split("_", 1)[1])

    user_data = await state.get_data()
    missed_students_id = user_data["missed_students_id"]
    attendants_id = user_data["attendants_id"][remap_num]
    missed_students_id.append(attendants_id)
    user_data["missed_students_id"] = missed_students_id

    await state.update_data(user_data)
    await get_attendant(callback.message, state)


@router.callback_query(F.data == "assign")
async def assign(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = user_data["token"]
    attendants_id = user_data["attendants_id"]

    status = await response.post_duty(token, attendants_id)

    if status == 201:
        await callback.message.edit_text("✅Дежурные установлены")
        await ut.clear_user_data(state, token, user_data["user"], user_data["group"])
    else:
        await callback.message.edit_text("✅Произошла неизвестная ошибка")


@router.message(lambda message: message.text == "Список дежурств")
async def duty_list(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = user_data["token"]

    status, duties = await response.get_duties(token)

    if status == 204:
        await message.answer("Список дежурств пуст", parse_mode="Markdown")

    msg = await ut.create_duties_msg("🧹*Дежурства:*\n\n", duties)
    await message.answer(msg, parse_mode="Markdown")


@router.message(lambda message: message.text == "Количество дежурств")
async def duty_count(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = user_data["token"]

    status, duties_count = await response.get_duties(token)

    if status == 204:
        await message.answer("Список дежурств пуст", parse_mode="Markdown")

    msg = "🧹*Количество дежурств:*\n\n"
    for duty in duties_count:
        msg += (
            f"*@{duty['attendant']['username']}* ({duty['attendant']['full_name']})\n"
            f"Дежурил(а) *{duty['attendant']['duties_count']} раз(а)*\n"
            f"Последнее дежурство: *{duty['attendant']['last_duty']}*\n\n"
        )

    await message.answer(msg, parse_mode="Markdown")
