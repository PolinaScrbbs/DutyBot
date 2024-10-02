import asyncio

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .ungroup import router

import response as response
import keyboards as kb


@router.message(lambda message: message.text == "Группа")
async def group_menu(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_data["back_in"] = {
        "function": group_menu.__name__,
        "params": {"message": message, "state": state},
    }

    token = user_data["token"]
    user = user_data["user"]

    status, group = await response.get_group(token)
    user_data["group"] = group
    await state.update_data(user_data)

    status, applications = await response.get_applications(
        token=token, application_type="На вступление в группу", group_id=group["id"]
    )

    applications_count = 0
    if status == 200:
        applications_count = len(applications)

    await message.answer(
        f"*{group['title'].upper()}*",
        parse_mode="Markdown",
        reply_markup=await kb.group_menu(applications_count),
    )


@router.callback_query(F.data == "students")
async def students(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = user_data["token"]

    status, students = await response.get_students(token)

    if status == 204:
        await callback.message.edit_text("Список студентов пуст")
    else:
        await callback.message.edit_text(
            "*Студенты*",
            parse_mode="Markdown",
            reply_markup=await kb.inline_students(students),
        )


@router.callback_query(lambda query: query.data.startswith("st_"))
async def student(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    student_username = callback.data.split("_", 1)[1]

    user_data = await state.get_data()
    token = user_data["token"]

    status, student = await response.get_user_by_username(student_username, token)
    student_first_name, student_last_name = student["full_name"].split()[:2]

    await callback.message.edit_text(
        f"*@{student['username']}*\n{student_first_name} {student_last_name}",
        parse_mode="Markdown",
        reply_markup=await kb.inline_student(student),
    )


@router.callback_query(lambda query: query.data.startswith("kick_"))
async def student_kick(callback: CallbackQuery, state: FSMContext):
    student_fields = callback.data.split("_")
    student_id = int(student_fields[1])

    user_data = await state.get_data()
    token = user_data["token"]

    await response.kick_student(student_id, token)

    await callback.message.edit_text(
        "✅ Пользователь удалён из группы.\nЕго история дежурств очищена",
    )

    await asyncio.sleep(3)
    await students(callback, state)
