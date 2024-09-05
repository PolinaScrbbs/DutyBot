from typing import List, Optional
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.utils.keyboard import (
    KeyboardBuilder,
    ReplyKeyboardBuilder,
    InlineKeyboardBuilder,
)


async def admin_menu(application_count: Optional[str]):
    admin_menu = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=f"Заявки {f'({application_count})' if application_count else ''}"
                )
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню",
    )

    return admin_menu
