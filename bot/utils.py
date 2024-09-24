from typing import Dict, Any

from aiogram.fsm.context import FSMContext


async def get_user_token(user_data: Dict[str, Any]) -> str:
    token = user_data.get("token", None)
    return token


async def clear_user_data(
    state: FSMContext, 
    token: str,
    user: Dict[str, Any]
) -> None:
    
    await state.clear()
    await state.update_data(
        {
            "token": token,
            "user": user
        }
    )
