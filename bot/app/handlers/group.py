from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import database.requests as rq

from database import get_async_session
from .ungroup import router


#Меню группы============================================================================================================


@router.message(lambda message: message.text == "Группа")
async def group_menu(message: Message, state: FSMContext):
    session = await get_async_session()
    user = await rq.get_user_by_username(session, message.from_user.username)
    group = await rq.get_group_by_id_with_students_and_applications(session, user.group_id, user.id)
    await session.close()

    await state.update_data(data={
        "user": user,
        "group": group
    })

    applications_count = len(group.applications)

    if applications_count != 0:
        applications_count = f'({applications_count})'
    else:
        applications_count = None
    
    await message.answer(f"*{group.title.upper()}*", parse_mode="Markdown", reply_markup=await kb.group_menu(applications_count))
    
    
@router.callback_query(F.data == 'students')
async def students(callback:CallbackQuery, state: FSMContext):
    data = await state.get_data()
    group = data['group']

    if group.students == []:
        await callback.message.edit_text('Список студентов пуст')

    else:
        await callback.message.edit_text('*Студенты*', parse_mode="Markdown", reply_markup=await kb.inline_students(group.students))

@router.callback_query(lambda query: query.data.startswith('st_'))
async def student(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    student_fields = callback.data.split('_')
    student_username = student_fields[2]

    try:
        session = await get_async_session()
        student = await rq.get_user_by_username(session, student_username)

        await callback.message.edit_text(
            f'*@{student.username}*\n{student.surname} {student.name}', 
            parse_mode='Markdown', 
            reply_markup=await kb.inline_student(student.id)
        )

    finally:
        await session.close()

@router.callback_query(lambda query: query.data.startswith('delete_student_'))
async def student_kick(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()
    student_fields = callback.data.split('_')
    student_id = int(student_fields[2])

    former_student = await rq.kick_student(session, student_id)

    await callback.message.edit_text(
        f'*@{former_student.username}* ({former_student.surname} {former_student.name}) выгнан(а) из группы',
        parse_mode='Markdown'
    )

    # await callback.message.answer(f"*{group_title.upper()}*", reply_markup=kb.group_menu, parse_mode="Markdown")

@router.callback_query(F.data == 'grp_applications')
async def group_applications_list(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()
    data = await state.get_data()
    group = data['group']

    applications = await rq.get_group_applications(session, group.id)

    if applications == []:
        await callback.message.edit_text('Список заявок пуст')
    else:
        await callback.message.edit_text('*Заявки*', parse_mode='Markdown', reply_markup=await kb.inline_group_applications(applications))

@router.callback_query(lambda query: query.data.startswith('grp_application_'))
async def group_application(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()

    callback_data_fields = callback.data.split('_')
    application_id = int(callback_data_fields[2])
    sending_id = int(callback_data_fields[3])

    application = await rq.get_application_by_id(session, application_id)
    user = await rq.get_user_by_id(session, sending_id)

    await callback.message.edit_text(f'Заявка @*{user.username}* ({user.surname} {user.name})', parse_mode='Markdown', reply_markup=await kb.inline_application(application))

@router.callback_query(lambda query: query.data.startswith('accept_application_'))
async def accept_group_application(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()

    callback_data_fields = callback.data.split('_')
    application_id = int(callback_data_fields[2])
    sending_id = int(callback_data_fields[3])

    application, msg = await rq.accept_application(session, application_id, sending_id)

    applications = await rq.get_group_applications(session, application.group_id)

    await callback.message.edit_text(f'{msg}', parse_mode='Markdown')

    if applications == []:
        await callback.message.edit_text('Список заявок пуст')
    else:
        await callback.message.edit_text('*Заявки*', parse_mode='Markdown', reply_markup=await kb.inline_group_applications(applications))

@router.callback_query(lambda query: query.data.startswith('rejected_application_'))
async def rejected_group_application(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()

    callback_data_fields = callback.data.split('_')
    application_id = int(callback_data_fields[2])
    sending_id = int(callback_data_fields[3])

    print(application_id, sending_id)

    application, msg = await rq.rejected_application(session, application_id, sending_id)

    applications = await rq.get_group_applications(session, application.group_id)

    await callback.message.edit_text(f'{msg}', parse_mode='Markdown')

    if applications == []:
        await callback.message.edit_text('Список заявок пуст')
    else:
        await callback.message.edit_text('*Заявки*', parse_mode='Markdown', reply_markup=await kb.inline_group_applications(applications))

    