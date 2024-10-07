import os
import aiohttp
from typing import Dict, Any, List, Optional
from aiogram import Bot
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN, DOWNLOAD_FOLDER


async def get_user_token(user_data: Dict[str, Any]) -> str:
    token = user_data.get("token", None)
    return token


async def clear_user_data(
    state: FSMContext,
    token: str,
    user: Dict[str, Any],
    group: Optional[Dict[str, Any]] = None,
) -> None:

    await state.clear()
    await state.update_data({"token": token, "user": user, "group": group})


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

async def get_user_avatar(bot: Bot, user_id: int):
    photos = await bot.get_user_profile_photos(user_id)
    if photos.total_count > 0:
        photo = photos.photos[0][-1]

        file_id = photo.file_id

        file_info = await bot.get_file(file_id)

        file_path = file_info.file_path

        url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

                    path = os.path.join(DOWNLOAD_FOLDER, f"avatars/{user_id}_avatar.jpg")
                    with open(path, 'wb') as f:
                        f.write(await resp.read())
                    return path

    return None
