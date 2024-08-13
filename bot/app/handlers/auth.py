from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.states as st
import database.requests as rq
from app.validators.registration import RegistrationValidator
from database import get_async_session

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
        username = data["username"]
        password = data["password"]
        confirm_password = data["confirm_password"]
        full_name = data["full_name"]
        
        validator = RegistrationValidator(full_name, password, confirm_password)
        error_message = await validator.validate()

        if error_message:
            await message.answer(f'❌*Ошибка:* {error_message}', parse_mode="Markdown", reply_markup=kb.start)
        else:
            try:
                session = await get_async_session()
                user = await rq.reg_user(session, username, password, full_name)
                await message.answer(f'✅ Пользователь *@{user.username}* успешно зарегистрирован.', parse_mode="Markdown", reply_markup=kb.start)
            except Exception as e:
                await message.answer(f'❌*Ошибка:* {e}', parse_mode="Markdown", reply_markup=kb.start)
    
    except Exception as e:
        await message.answer(f'❌*Ошибка:* {str(e)}', parse_mode="Markdown", reply_markup=kb.start)

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
        # msg = "❌ Неверный логин или пароль"
        # keyboard = None

        user = await rq.auth_user(session, login, password)
        
        keyboard = kb.elder_main
            
        if user.group_id == None:
            keyboard = kb.ungroup_main

        await message.answer(f"*@{user.username}*, авторизация завершена ✌️", parse_mode="Markdown", reply_markup=keyboard)
        # else:
        #     await message.answer("❌ Неверный логин или пароль")

    except Exception as e:
        await message.answer(f'❌ Ошибка авторизации: {e}', parse_mode="Markdown", reply_markup=kb.start)
    finally:
        await session.close()
        await state.clear()