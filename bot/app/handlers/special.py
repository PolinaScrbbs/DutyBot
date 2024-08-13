from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .group import router

@router.callback_query(F.data == 'cancel')
async def catalog(callback:CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('✅Отменено')