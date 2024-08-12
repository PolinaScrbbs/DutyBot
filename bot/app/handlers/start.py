from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import get_async_session
from .. import User
import app.keyboards as kb


router = Router()

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
                if user.created_group == []:
                    keyboard = kb.ungroup_main
                else:
                    keyboard = kb.elder_main
            await message.answer(msg, reply_markup=keyboard)
        else:
            await message.answer(msg, reply_markup=keyboard)
    finally:
        await session.close()