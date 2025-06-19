import os
import aiohttp
from typing import Dict, Any, Union, Optional
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .config import config as conf


async def get_user_token(
    event: Union[Message, CallbackQuery],
    user_data: Dict[str, Any],
    show_error: bool = True,
) -> Optional[str]:
    try:
        token = user_data.get("token")
        if token:
            return token
        if isinstance(event, Message) & show_error:
            await event.answer("Ошибка авторизации")
        elif isinstance(event, CallbackQuery) & show_error:
            await event.message.answer("Ошибка авторизации")
    except Exception:
        if isinstance(event, Message) & show_error:
            await event.answer("Ошибка авторизации")
        elif isinstance(event, CallbackQuery) & show_error:
            await event.message.answer("Ошибка авторизации")


async def clear_user_data(
    state: FSMContext,
    token: str,
    user: Dict[str, Any],
    group: Optional[Dict[str, Any]] = None,
) -> None:

    await state.clear()
    await state.update_data({"token": token, "user": user, "group": group})


async def create_duties_msg(initial_line: str, duties: dict) -> str:
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


async def get_user_avatar(bot: Bot, user_id: int) -> Optional[str]:
    photos = await bot.get_user_profile_photos(user_id, 0, 1)
    if photos.total_count > 0:
        photo = photos.photos[0][-1]

        file_id = photo.file_id

        file_info = await bot.get_file(file_id)

        file_path = file_info.file_path

        url = f"https://api.telegram.org/file/bot{conf.bot_token}/{file_path}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    avatars_folder = os.path.join(conf.media_folder, "avatars")
                    os.makedirs(avatars_folder, exist_ok=True)

                    path = os.path.join(avatars_folder, f"{user_id}_avatar.jpg")
                    with open(path, "wb") as f:
                        f.write(await resp.read())
                    return path

    default_avatar_path = None
    return default_avatar_path
