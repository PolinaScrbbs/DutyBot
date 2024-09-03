from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import get_async_session
import app.keyboards as kb
import database.requests as rq

from .. import Role

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    session = await get_async_session()
    username = message.from_user.username
    try:
        user = await rq.get_user_by_username(session, username)

        msg = "Привет👋\nВыбери пункт из меню🔍"
        keyboard = kb.start

        if user and await rq.auth_check(session, user.id):
            msg = f"С возвращением, *{user.name}*👋 \nВыбери пункт из меню🔍"
            keyboard = kb.ungroup_main

            if user.group_id != None:
                group = await rq.get_group_by_id_with_students_and_applications(
                    session, user.group_id, user.id
                )

                await state.update_data(
                    {message.from_user.id: {"user": user, "group": group}}
                )

                if user.role == Role.STUDENT:
                    keyboard = kb.student_main

                elif user.role == Role.ELDER:
                    keyboard = kb.elder_main

        await message.answer(msg, reply_markup=keyboard, parse_mode="Markdown")

    finally:
        await session.close()
