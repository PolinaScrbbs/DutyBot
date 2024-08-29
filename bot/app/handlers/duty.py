from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.utils as ut
import database.requests as rq

from database import get_async_session
from database.models import Role
from .group import router

@router.message(lambda message: message.text == "Дежурства")
async def group_menu(message: Message, state: FSMContext):
    data = await state.get_data()
    user_data = data.get(message.from_user.id, {})
    user = user_data.get("user")
        
    msg = "Выберите пункт из меню"
    keyboard = kb.duty_menu

    if user.role == Role.STUDENT:
        session = await get_async_session()
        keyboard = kb.student_main
        
        duties, last_duty = await rq.get_user_duties(session, user.id)
        if duties:
            duties_count = await user.duties_count(session=session)
            last_duty_date = await last_duty.formatted_date

            msg = (
                f"Общее количество дежурств *{duties_count}*\n"
                f"Последнее дежурство *{last_duty_date}*\n\n"
            )

            msg = await ut.create_duties_msg(msg, duties)      
        else:
            msg = "У вас нет дежурств"

        await session.close()
    await message.answer(msg, parse_mode="Markdown", reply_markup=keyboard)


@router.message(lambda message: message.text == "Назначить дежурных")
async def get_attendant(message: Message, state: FSMContext):
    data = await state.get_data()
    user_data = data.get(message.from_user.id, None)
    user = user_data["user"]
    group = user_data["group"]

    if user.role == Role.ELDER:
        session = await get_async_session()

        students = data.get('students', None)
        if students is None:
            students = await rq.get_students(session, group.id)
            user_data['students'] = students
            await state.update_data({
                message.from_user.id: user_data
            })

        attendants = await rq.get_attendants(session, students)
        user_data['attendants'] = attendants
        await state.update_data({
            message.from_user.id: user_data
        })
        await session.close()

        await message.answer(
            f"🧹*Дежурные*",
            parse_mode="Markdown",
            reply_markup=await kb.attendants(
                f"{attendants[0].surname} {attendants[0].name}", 
                f"{attendants[1].surname} {attendants[1].name}"
            )   
        )
    else:
        await message.answer("У вас не достаточно прав")

@router.callback_query(F.data == 'attendants_assign')
async def assign_attendants(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()

    data = await state.get_data()
    user_data = data.get(callback.from_user.id, None)
    attendants = user_data.get('attendants')

    await rq.put_duty(session, attendants)

    await callback.message.edit_text('✅Дежурные установлены')
    await state.clear()

@router.callback_query(lambda query: query.data.startswith('replace_attendant_'))
async def replace_attendant(callback: CallbackQuery, state: FSMContext):
    attendant_fields = callback.data.split('_')
    attendant_number = int(attendant_fields[2])
    
    data = await state.get_data()
    user_data = data.get(callback.from_user.id, {})
    group = user_data.get("group")
    students = user_data.get('students')

    if len(students) >= 3:
        attendants = user_data.get('attendants', [])
        attendant = attendants[attendant_number]
        students = [student for student in students if student != attendant]

        user_data['students'] = students
        await state.update_data({
            callback.from_user.id: user_data
        })

        session = await get_async_session()
        attendants = await rq.get_attendants(session, students)
        user_data['attendants'] = attendants
        await state.update_data({
            callback.from_user.id: user_data
        })
        await session.close()

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

        await state.clear()
        await state.update_data({
            callback.from_user.id: {
                "user": user_data.get("user"),
                "group": group
            }
        })

@router.message(lambda message: message.text == "Список дежурств")
async def duty_list(message: Message, state: FSMContext):
    session = await get_async_session()

    data = await state.get_data()
    user_data = data.get(message.from_user.id, None)
    group = user_data["group"]

    duties = await rq.get_group_duties(session, group.id)
    msg = await ut.create_duties_msg("🧹*Дежурства:*\n\n", duties)

    await message.answer(msg, parse_mode="Markdown")

@router.message(lambda message: message.text == "Количество дежурств")
async def duty_count(message: Message, state: FSMContext):
    session = await get_async_session()

    data = await state.get_data()
    user_data = data.get(message.from_user.id, None)
    group = user_data["group"]

    duties_count = await rq.get_group_duties_count(session, group.id)

    msg = "🧹*Количество дежурств:*\n\n"
    
    for duty in duties_count:
        msg += (
            f"*@{duty['username']}* ({duty['full_name']})\n"
            f"Дежурил(а) *{duty['duties_count']} раз(а)*\n"
            f"Последнее дежурство: *{duty['last_duty_date'].strftime('%H:%M %d-%m-%Y')}*\n\n"
        )

    await message.answer(msg, parse_mode="Markdown")


    