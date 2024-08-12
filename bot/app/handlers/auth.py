from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from sqlalchemy import select
from sqlalchemy.orm import selectinload

import app.keyboards as kb
import app.states as st
import database.requests as rq
from app.validators.registration import RegistrationValidator
from database import get_async_session

from .. import User, Token
from .start import router


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
        
        keyboard = kb.elder_main

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