from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils import markdown

from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

import app.keyboards as kb
import app.states as st
import app.utils as ut
from . import User, Token, Role, ApplicationType
from app.validators.registration import RegistrationValidator
from database import get_async_session
import database.response as rq

import logging
logging.basicConfig(level=logging.INFO)

router = Router()

#Старт
@router.message(CommandStart())
async def cmd_start(message: Message):
    session = await get_async_session()
    try:
        result = await session.execute(
            select(User)
            .where(User.username == message.from_user.username)
            .options(selectinload(User.created_group), selectinload(User.tokens))
        )
        user = result.unique().scalar_one_or_none()
        
        msg = 'Привет👋\nВыбери пункт из меню🔍'
        keyboard = kb.start

        if user:
            if user.get_token():
                msg = 'С возвращением👋\nВыбери пункт из меню🔍'
                print(user.created_group)
                if user.created_group == []:
                    keyboard = kb.ungroup_main
                else:
                    keyboard = kb.main
            await message.answer(msg, reply_markup=keyboard)
        else:
            await message.answer(msg, reply_markup=keyboard)
    finally:
        await session.close()


#Регистрация============================================================================================================


@router.message(lambda message: message.text == "Регистрация")
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(username=message.from_user.username)
    await state.set_state(st.Registration.full_name)
    await message.answer('👨‍🎓Введите ФИО', reply_markup=kb.cancel)

@router.message(st.Registration.full_name)
async def get_password(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(st.Registration.password)
    await message.answer('🔑Создайте пароль', reply_markup=kb.cancel)

@router.message(st.Registration.password)
async def get_confirm_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await state.set_state(st.Registration.confirm_password)
    await message.answer('🔑Подтвердите пароль ', reply_markup=kb.cancel)

@router.message(st.Registration.confirm_password)
async def registration(message: Message, state: FSMContext):
    try:
        await state.update_data(confirm_password=message.text)
        data = await state.get_data()
        full_name = data["full_name"]
        password = data["password"]
        confirm_password = data["confirm_password"]

        validator = RegistrationValidator(full_name, password, confirm_password)
        error_message = await validator.validate()

        if error_message:
            await message.answer(f'❌*Ошибка1:* {error_message}', parse_mode="Markdown", reply_markup=kb.start)
        else:
            session = await get_async_session()
            parts = full_name.split()
            surname, name, patronymic = parts
            try:
                await rq.register_user(
                    session,
                    message.from_user.username,
                    password,
                    name,
                    surname,
                    patronymic
                )

                await message.answer(f'✅ Пользователь *@{message.from_user.username}* успешно зарегистрирован.', parse_mode="Markdown", reply_markup=kb.start)
            except Exception as e:
                await message.answer(f'❌*Ошибка2:* {e}', parse_mode="Markdown", reply_markup=kb.start)
    
    except Exception as e:
        await message.answer(f'❌*Ошибка3:* {str(e)}', parse_mode="Markdown", reply_markup=kb.start)

    finally:
        await session.close()
        await state.clear()


#Авторизация============================================================================================================


@router.message(lambda message: message.text == "Авторизация")
async def get_password(message: Message, state: FSMContext):
    await state.set_state(st.Auth.password)
    await message.answer('🔑Введите пароль', reply_markup=kb.cancel)

@router.message(st.Auth.password)
async def authorazation(message: Message, state: FSMContext):
    login = message.from_user.username
    password = message.text
    
    try:
        session = await get_async_session()
        result = await session.execute(
                select(User).filter(User.username == login)
                .options(selectinload(User.groups))
            )
        user = result.scalar_one_or_none()
        
        keyboard = kb.main

        if user and user.check_password(password):
            token = user.generate_token()
            token = Token(user_id=user.id, token=token)
            session.add(token)
            await session.commit()

            if not user.groups:
                keyboard = kb.ungroup_main

            await message.answer(f"*@{message.from_user.username}*, авторизация завершена ✌️", parse_mode="Markdown", reply_markup=keyboard)
        else:
            await message.answer("❌ Неверный логин или пароль")

    except Exception as e:
        await message.answer(f'❌Ошибка авторизации {e}')
    finally:
        await session.close()
        await state.clear()


#Создание группы============================================================================================================


@router.message(lambda message: message.text == "Создать группу")
async def group_create(message: Message, state: FSMContext):
    session = await get_async_session()
    tg_username = message.from_user.username
    try:
        result = await session.execute(
            select(User)
            .where(User.username == tg_username)
            .options(selectinload(User.created_group), selectinload(User.tokens)))
        
        user = result.unique().scalar_one_or_none()

        if not user:
            await message.answer(f'Пользователь @{tg_username} не найден, пройдите регистрацию', reply_markup=kb.start)

        elif user.tokens is None:
            await message.answer(f'Пройдите авторизацию', reply_markup=kb.start)

        elif user.role is Role.ELDER:
            if user.created_group == []:
                await message.answer(f'Введите название группы (Не номер)')
                await state.set_state(st.GroupCreate.title)
            else:
                await message.answer(f'"Староста" может создать только 1 группу', reply_markup=kb.main)
        else:
            await message.answer(f'Сначала необходимо стать "Старостой", подайте заявку, её рассмотрят в ближайшее время', reply_markup=kb.ungroup_main)

    finally:
        await session.close()

@router.message(st.GroupCreate.title)
async def group_title(message: Message, state: FSMContext):
    await state.update_data(creator=message.from_user.username)
    await state.update_data(title=message.text)
    
    await message.answer('Выберите свою специальность', reply_markup=kb.specializations)

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

    course_number = int(callback.data.split('_')[2])
    await callback.message.edit_text(f'Вы выбрали *{course_number} курс*', parse_mode='Markdown')

    session= await get_async_session()
    data = await state.get_data()
    title = data["title"]
    specialization = await rq.get_specialization(data["specialization"])
    username = data["creator"]

    group = await rq.create_group(session, title, specialization, course_number, username)

    if group:
        await callback.message.answer(text=f'Группа *{group.title}* для *{group.course_number}* курса создана. Староста *@{username}*', parse_mode='Markdown' ,reply_markup=kb.main)


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
async def group_join(message: Message):
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

@router.callback_query(F.data == 'cancel')
async def clear(callback:CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('✅Отменено')