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
    user = await rq.get_user(session, message.from_user.username)
    group = await rq.get_group_by_id_with_students(session, user.group_id)
    await session.close()

    await state.update_data(data={
        "user": user,
        "group": group
    })
    
    await message.answer(f"*{group.title.upper()}*", reply_markup=kb.group_menu, parse_mode="Markdown")
    
    
@router.callback_query(F.data == 'students')
async def catalog(callback:CallbackQuery, state: FSMContext):
    data = await state.get_data()
    group = data['group']
    
    await callback.message.edit_text('*Студенты*', parse_mode="Markdown", reply_markup=await kb.inline_students(group.students))

    