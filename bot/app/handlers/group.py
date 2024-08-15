from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.states as st
import app.utils as ut
import database.requests as rq

from .. import Role, ApplicationType
from database import get_async_session
from .ungroup import router


#Меню группы============================================================================================================


@router.message(lambda message: message.text == "Группа")
async def group_menu(message: Message, state: FSMContext):
    session = await get_async_session()
    user = await rq.get_user_by_username(session, message.from_user.username)
    group = await rq.get_group_by_id_with_students(session, user.group_id, user.id)
    await session.close()

    await state.update_data(data={
        "user": user,
        "group": group
    })
    
    await message.answer(f"*{group.title.upper()}*", reply_markup=kb.group_menu, parse_mode="Markdown")
    
    
@router.callback_query(F.data == 'students')
async def students(callback:CallbackQuery, state: FSMContext):
    data = await state.get_data()
    group = data['group']
    
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
    print(student_fields, student_id)

    former_student = await rq.kick_student(session, student_id)

    await callback.message.edit_text(
        f'*@{former_student.username}* ({former_student.surname} {former_student.name}) выгнан(а) из группы',
        parse_mode='Markdown'
    )

    # await callback.message.answer(f"*{group_title.upper()}*", reply_markup=kb.group_menu, parse_mode="Markdown")

@router.callback_query(F.data == 'grp_applications')
async def group_application_list(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()
    data = await state.get_data()
    group = data['group']

    applications = await rq.get_group_applications(session, group.id)

    await callback.message.edit_text('*Заявки*', parse_mode='Markdown', reply_markup=await kb.inline_group_applications(applications))

    