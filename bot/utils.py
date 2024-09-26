from typing import Dict, Any, List

from aiogram.fsm.context import FSMContext


async def get_user_token(user_data: Dict[str, Any]) -> str:
    token = user_data.get("token", None)
    return token


async def clear_user_data(state: FSMContext, token: str, user: Dict[str, Any]) -> None:

    await state.clear()
    await state.update_data({"token": token, "user": user})


async def create_duties_msg(initial_line: str, duties: List[dict]) -> str:
    msg = initial_line

    for duty in duties:
        attendant_username = duty["attendant"]["username"]
        attendant_full_name = duty["attendant"]["full_name"]
        duty_date = duty["date"]
        msg += (
            f"👨‍🎓 *@{attendant_username}* ({attendant_full_name})\n"
            f"Дежурил(а) ⏰*{duty_date}*\n\n"
        )

    return msg
