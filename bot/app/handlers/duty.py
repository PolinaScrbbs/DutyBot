from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import database.requests as rq

from database import get_async_session
from .group import router

@router.message(lambda message: message.text == "Дежурства")
async def group_menu(message: Message, state: FSMContext):
    session = await get_async_session()
    user = await rq.get_user_by_username(session, message.from_user.username)
    group = await rq.get_group_by_id_with_students_and_applications(session, user.group_id, user.id)
    await session.close()

    await state.update_data(data={
        # "user": user,
        "group": group
    })
    
    await message.answer("Выберите пунк из меню", parse_mode="Markdown", reply_markup=kb.duty_menu)


@router.message(lambda message: message.text == "Назначить дежурных")
async def get_attendant(message: Message, state: FSMContext):
    session = await get_async_session()
    data = await state.get_data()
    group = data['group']

    students = data.get('students', None)

    if students is None:
        students = await rq.get_students(session, group.id)
        await state.update_data(students=students)

    attendants = await rq.get_attendants(students)
    await state.update_data(attendants=attendants)

    await message.answer(
        f"🧹*Дежурные*",
        parse_mode="Markdown",
        reply_markup=await kb.attendants(
            f"{attendants[0].surname} {attendants[0].name}", 
            f"{attendants[1].surname} {attendants[1].name}"
        )   
    )

@router.callback_query(F.data == 'attendants_assign')
async def assign_attendants(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()
    data = await state.get_data()
    attendants = data['attendants']

    await rq.put_duty(session, attendants)

    await callback.message.edit_text('✅Дежурные установлены', reply_markup=kb.elder_main)
    await state.clear()

@router.callback_query(lambda query: query.data.startswith('replace_attendant_'))
async def replace_attendant(callback: CallbackQuery, state: FSMContext):
    attendant_fields = callback.data.split('_')
    attendant_number = int(attendant_fields[2])
    
    data = await state.get_data()
    students = data['students']

    if len(students) >= 3:
        attendant = data['attendants'][attendant_number]
        students = [student for student in students if student != attendant]
        await state.update_data(students=students)

        attendants = await rq.get_attendants(students)
        await state.update_data(attendants=attendants)

        await callback.message.edit_text(
            f"🧹*Дежурные*",
            parse_mode="Markdown", 
            reply_markup=await kb.attendants(
                f"{attendants[0].surname} {attendants[0].name}", 
                f"{attendants[1].surname} {attendants[1].name}"
            )
        )
    else:
        await callback.message.edit_text("*Куда гонишь, брат?*", parse_mode="Markdown")

        group = data['group']

        await state.clear()
        await state.update_data(group=group)




    