import asyncio

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .ungroup import router

from .. import response
from .. import keyboards as kb
from .. import states as st
from .. import utils as ut


@router.message(lambda message: message.text == "Группа")
async def group_menu(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_data["back_in"] = {
        "function": group_menu.__name__,
        "params": {"message": message, "state": state},
    }

    token = await ut.get_user_token(message, user_data)

    if token:
        status, group = await response.get_group(token)

        if status != 200:
            await message.answer("⚠️ Вы пока не состоите ни в одной группе.")
        else:
            user_data["group"] = group
            await state.update_data(user_data)

            status, applications = await response.get_applications(
                token=token,
                application_type="На вступление в группу",
                group_id=group["id"],
            )

            applications_count = 0
            if status == 200:
                applications_count = len(applications)

            await message.answer(
                f"📚 *{group['title'].upper()}*",
                parse_mode="Markdown",
                reply_markup=await kb.group_menu(applications_count),
            )


@router.callback_query(F.data == "students")
async def students(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)

    if token:
        status, students_list = await response.get_students(token)

        if status in [204, 404]:
            await callback.message.edit_text("👥 Список студентов пока пуст.")
        else:
            await callback.message.edit_text(
                "👥 *Студенты группы*",
                parse_mode="Markdown",
                reply_markup=await kb.inline_students(students_list),
            )


@router.callback_query(lambda query: query.data.startswith("st_"))
async def student(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    student_username = callback.data.split("_", 1)[1]

    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)

    if token:
        status, student_dict = await response.get_user_by_username(
            student_username, token
        )
        student_first_name, student_last_name = student_dict["full_name"].split()[:2]

        await callback.message.edit_text(
            f"👤 *@{student_dict['username']}*\n{student_first_name} {student_last_name}",
            parse_mode="Markdown",
            reply_markup=await kb.inline_student(student_dict),
        )


@router.callback_query(lambda query: query.data.startswith("kick_"))
async def student_kick(callback: CallbackQuery, state: FSMContext):
    student_fields = callback.data.split("_")
    student_id = int(student_fields[1])

    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)

    if token:
        await response.kick_student(student_id, token)

        await callback.message.edit_text(
            "✅ Пользователь успешно удалён из группы.\nИстория его дежурств очищена.",
        )

        await asyncio.sleep(3)
        await students(callback, state)


@router.callback_query(F.data == "settings")
async def group_settings(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)

    if token:
        group = user_data.get("group")
        await callback.message.edit_text(
            f"⚙️ *Информация о группе:*\n\n"
            f"*Название:* {group['title']}\n"
            f"*Специальность:* {group['specialization']}\n"
            f"*Курс:* {group['course_number']} курс\n"
            f"*Дата создания:* {group['created_at'][:10]}",
            parse_mode="Markdown",
            reply_markup=kb.group_update,
        )


@router.callback_query(lambda query: query.data.startswith("update_group_"))
async def handle_group_update(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split("update_group_")[1]

    match action:
        case "title":
            await callback.message.edit_text("✏️ Введите новое название группы:")
            await state.set_state(st.GroupUpdate.title)
        case "specialization":
            user_data = await state.get_data()
            token = await ut.get_user_token(callback, user_data)
            status, specializations = await response.get_specializations(token)
            await callback.message.edit_text(
                "📋 Выберите новую специальность:",
                reply_markup=await kb.create_specializations_keyboard(
                    specializations, "up_spec:"
                ),
            )
        case "course_number":
            await callback.message.edit_text(
                "🔢 Выберите новый номер курса:",
                reply_markup=await kb.course_number("up_course_number:"),
            )


@router.message(st.GroupUpdate.title)
async def update_group_title(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(message, user_data)

    title = message.text
    status, err = await response.patch_group(token, {"title": title})

    await ut.clear_user_data(state, token, user_data["user"], user_data["group"])

    if status == 200:
        await message.answer("✅ Название группы успешно обновлено.")
    else:
        await message.answer(f"❌ Ошибка при обновлении названия: {err['detail']}")

    await group_menu(message, state)


@router.callback_query(F.data.startswith("up_spec:"))
async def update_group_specialization(callback: CallbackQuery, state: FSMContext):
    specialization = callback.data.split(":")[1]
    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)

    status, err = await response.patch_group(token, {"specialization": specialization})

    if status == 200:
        await callback.message.edit_text("✅ Специальность успешно обновлена.")
    else:
        await callback.message.edit_text(
            f"❌ Ошибка при обновлении специальности: {err['detail']}"
        )

    await group_menu(callback.message, state)


@router.callback_query(F.data.startswith("up_course_number:"))
async def update_group_course(callback: CallbackQuery, state: FSMContext):
    course = int(callback.data.split(":")[1])
    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)

    status, err = await response.patch_group(token, {"course_number": course})

    if status == 200:
        await callback.message.edit_text("✅ Номер курса успешно обновлён.")
    else:
        await callback.message.edit_text(
            f"❌ Ошибка при обновлении номера курса: {err['detail']}"
        )

    await group_menu(callback.message, state)


@router.callback_query(F.data == "delete_group")
async def group_settings(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)
    if token:
        status, err = await response.delete_group(token)
        user_data["user"]["group_id"] = None
        await ut.clear_user_data(state, token, user_data["user"], None)
        if status == 200:
            await callback.message.edit_text("✅ Группа успешно удалена.")
            await callback.message.answer(
                f"👋 Добро пожаловать обратно, @{callback.message.from_user.username}!\n"
                f"Выберите пункт из меню 🔍",
                reply_markup=kb.ungroup_main,
            )

        else:
            await callback.message.edit_text(
                f"❌ Не удалось удалить группу: {err['detail']}"
            )
