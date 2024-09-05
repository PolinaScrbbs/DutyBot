from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import database.requests as rq

from database import get_async_session
from .ungroup import router


@router.message(lambda message: message.text == "Группа")
async def group_menu(message: Message, state: FSMContext):
    session = await get_async_session()
    user = await rq.get_user_by_username(session, message.from_user.username)
    group = await rq.get_group_by_id_with_students_and_applications(
        session, user.group_id, user.id
    )
    await session.close()

    await state.update_data({message.from_user.id: {"user": user, "group": group}})

    applications_count = len(group.applications)

    await message.answer(
        f"*{group.title.upper()}*",
        parse_mode="Markdown",
        reply_markup=await kb.group_menu(applications_count),
    )


@router.message(lambda message: message.text == "Профиль")
async def profile(message: Message, state: FSMContext):
    session = await get_async_session()
    data = await state.get_data()
    telegram_id = message.from_user.id

    if telegram_id not in data:
        await message.answer("Ваши данные не найдены. Пожалуйста, начните сначала.")
        return

    user = data[telegram_id]["user"]
    group = data[telegram_id]["group"]

    user_photos = await message.bot.get_user_profile_photos(user_id=telegram_id)

    profile_title = "<b>👤 Мой Профиль</b>"
    username = user.username
    full_name = await user.full_name
    group_name = group.title
    avatar_url = None
    icon = None
    user_link = None

    if user.username != message.from_user.username:
        if user_photos.total_count > 0:
            file_id = user_photos.photos[0][-1].file_id

            file = await message.bot.get_file(file_id)
            avatar_url = (
                f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"
            )
            icon = "🖼️"

        profile_title = (
            f"<b>👤 Профиль</b> <i><a href='{user_link}'>@{username}</a></i>"
        )

        user_link = f"https://t.me/{username}"

    last_three_duties = await rq.get_last_three_duties(session, user.id)
    await session.close()

    profile_text = f"""
{profile_title}{f'<a href="{avatar_url}">{icon}</a>' if avatar_url else ''}\n
<b>Полное имя:</b> {full_name}
{f"<b>Группа:</b> {group_name}" if group_name else "Не состоит в группе"}
    """

    if last_three_duties:
        profile_text += "\n<b>Последние дежурства:</b>\n"
        for duty in last_three_duties:
            profile_text += f"🔸 {duty['date']}\n"
    else:
        profile_text += "\n<b>Последние дежурства:</b> Нет записей\n"

    await message.answer(profile_text, parse_mode="HTML")


@router.callback_query(F.data == "students")
async def students(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    group = data[callback.from_user.id]["group"]

    if not group.students:
        await callback.message.edit_text("Список студентов пуст")
    else:
        await callback.message.edit_text(
            "*Студенты*",
            parse_mode="Markdown",
            reply_markup=await kb.inline_students(group.students),
        )


@router.callback_query(lambda query: query.data.startswith("st_"))
async def student(callback: CallbackQuery):
    await callback.message.delete_reply_markup()
    student_fields = callback.data.split("_")
    student_id = int(student_fields[1])

    try:
        session = await get_async_session()
        student = await rq.get_user_by_id(session, student_id)

        await callback.message.edit_text(
            f"*@{student.username}*\n{student.surname} {student.name}",
            parse_mode="Markdown",
            reply_markup=await kb.inline_student(student.id),
        )

    finally:
        await session.close()


@router.callback_query(lambda query: query.data.startswith("delete_student_"))
async def student_kick(callback: CallbackQuery):
    session = await get_async_session()
    student_fields = callback.data.split("_")
    student_id = int(student_fields[2])

    former_student = await rq.kick_student(session, student_id)

    await callback.message.edit_text(
        f"*@{former_student.username}* ({former_student.surname} {former_student.name}) выгнан(а) из группы",
        parse_mode="Markdown",
    )
