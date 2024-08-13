from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import bot.app.keyboards as kb
import app.states as st
import app.utils as ut
import database.requests as rq

from .. import Role, ApplicationType
from database import get_async_session
from .auth import router


#Создание группы============================================================================================================


@router.message(lambda message: message.text == "Создать группу")
async def group_create(message: Message, state: FSMContext):
    session = await get_async_session()
    username = message.from_user.username
    try:
        user = await rq.get_user(session, username)

        if not user:
            await message.answer(f'Пользователь @{username} не найден, пройдите регистрацию', reply_markup=kb.start)

        elif not await rq.auth_check(session, user.id):
            await message.answer(f'Пройдите авторизацию', reply_markup=kb.start)

        elif user.role is not Role.ELDER:
            await message.answer(f'Сначала необходимо стать "Старостой", подайте заявку, её рассмотрят в ближайшее время', reply_markup=kb.ungroup_main)

        elif user.group_id != None:
            await message.answer(f'"Староста" может создать только 1 группу', reply_markup=kb.ungroup_main)

        else:
            await message.answer(f'Введите название группы (Не номер)')
            await state.set_state(st.GroupCreate.title)

    finally:
        await session.close()

@router.message(st.GroupCreate.title)
async def group_title(message: Message, state: FSMContext):
    
    title = message.text
    await state.update_data(creator=message.from_user.username)
    await state.update_data(title=title)

    try:
        session = await get_async_session()
        if await rq.get_group_by_title(session, title):
            await session.rollback()
            raise Exception("Группа с таким названием уже существует")
        else: 
            await message.answer('Выберите свою специальность', reply_markup=kb.specializations)

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        await message.answer(f'Введите название группы (Не номер)')
    finally:
        await session.close()
    
    

@router.callback_query(lambda query: query.data.startswith('spec_'))
async def group_specialization(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()

    specialization = callback.data.split('_', 1)[1]
    await callback.message.edit_text(f'Вы выбрали *{specialization}*', parse_mode='Markdown')
    await state.update_data(specialization=specialization)

    await callback.message.answer('Выберите свой курс обучения', reply_markup=kb.course_number)

@router.callback_query(lambda query: query.data.startswith('course_number_'))
async def group_course_number(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    try:
        course_number = int(callback.data.split('_')[2])
        await callback.message.edit_text(f'Вы выбрали *{course_number} курс*', parse_mode='Markdown')

        session= await get_async_session()
        data = await state.get_data()
        title = data["title"]
        specialization = await rq.get_specialization(data["specialization"])
        username = data["creator"]
        
        group = await rq.create_group(session, title, specialization, course_number, username)

        if group:
            await callback.message.answer(
                text=f'Группа *{group.title}* для *{group.course_number}* курса создана. Староста *@{username}*',
                parse_mode='Markdown',
                reply_markup=kb.main
            )

    except Exception as e:
        await callback.message.answer(f"{e}")

#Вступление в группу ============================================================================================================>


@router.message(lambda message: message.text == "Вступить в группу")
async def group_join(message: Message, state: FSMContext):
    try:
        session = await get_async_session()
        user = await rq.get_user(session, message.from_user.username)
        groups_without_application_from_user = await rq.get_groups_without_application_from_user(session, user.id)

        await state.update_data(user_id=user.id)

        if groups_without_application_from_user != []:
            await message.answer('Выберите группу', parse_mode='Markdown', reply_markup=await kb.inline_groups(groups_without_application_from_user))
        else:
            await message.answer('Группы не найдены', parse_mode='Markdown', reply_markup=kb.ungroup_main)

    finally:
        await session.close()

@router.callback_query(lambda query: query.data.startswith('group_'))
async def group_application(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()

    session = await get_async_session()
    data = await state.get_data()
    user_id = data["user_id"]
    group_fields = callback.data.split('_')
    group_id = int(group_fields[1])
    group_title = group_fields[2]

    request = await rq.send_application(session, ApplicationType.GROUP_JOIN, user_id, group_id)

    if request:
        await callback.message.edit_text(f'Заявка на вступление в *{group_title}* отправлена', parse_mode='Markdown')
    else:
        await callback.message.edit_text(f'Не удалось отправить заявку на вступление')


#Стать старостой ============================================================================================================>


@router.message(lambda message: message.text == "Стать старостой")
async def elder_application(message: Message):
    try:
        session = await get_async_session()
        user = await rq.get_user(session, message.from_user.username)

        application = await rq.get_application(session, ApplicationType.BECOME_ELDER, user.id, None)
        msg = f'Ваша заявка была отправлена *{ut.format_datetime(application.last_update_at)}*'
        
        if application is None:
            application = await rq.send_application(session, ApplicationType.BECOME_ELDER, user.id, None)
            msg = 'Заявка на получение роли *"Староста"* отправлена'

        await message.answer(msg, parse_mode='Markdown')

    finally:
        await session.close()