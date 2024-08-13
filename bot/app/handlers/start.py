from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import get_async_session
import bot.app.keyboards as kb
import database.requests as rq

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    session = await get_async_session()
    username = message.from_user.username
    try:
        user = await rq.get_user(session, username)
        
        msg = 'Привет👋\nВыбери пункт из меню🔍'
        keyboard = kb.start

        if user and await rq.auth_check(session, user.id):
            msg = f'С возвращением *{username}*👋 \nВыбери пункт из меню🔍'
            keyboard = kb.main
            
            group = await rq.get_group_by_id(session, user.group_id)

            if group == None:
                keyboard = kb.ungroup_main

        await message.answer(msg, reply_markup=keyboard, parse_mode="Markdown")
        
    finally:
        await session.close()