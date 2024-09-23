from typing import Dict, Any

from aiogram.fsm.context import FSMContext


async def get_user_data(state: FSMContext, user_id: int) -> Dict[str, Any]:
    data = await state.get_data()
    return data.get(user_id, {})
