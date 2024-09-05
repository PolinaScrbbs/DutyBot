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


async def inline_applications(applications):
    keyboard = InlineKeyboardBuilder()

    len_range = (
        len(applications) if len(applications) % 2 == 0 else len(applications) - 1
    )

    for j in range(0, len_range, 2):
        keyboard.row(
            InlineKeyboardButton(
                text=f"@{applications[j].sending.username} ({applications[j].sending.surname} {applications[j].sending.name})",
                callback_data=f"application_{applications[j].id}_{applications[j].sending.id}",
            ),
            InlineKeyboardButton(
                text=f"{applications[j + 1].sending.username} ({applications[j + 1].sending.surname} {applications[j + 1].sending.name})",
                callback_data=f"application_{applications[j + 1].id}_{applications[j + 1].sending.id}",
            ),
        )

    if len(applications) % 2 != 0:
        keyboard.row(
            InlineKeyboardButton(
                text=f"@{applications[-1].sending.username} ({applications[-1].sending.surname} {applications[-1].sending.name})",
                callback_data=f"application_{applications[-1].id}_{applications[-1].sending.id}",
            )
        )

    keyboard.row(InlineKeyboardButton(text="❌ Закрыть", callback_data="close"))

    return keyboard.as_markup()


async def inline_application(application):
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(
            text="Принять",
            callback_data=f"accept_application_{application.id}_{application.sending_id}",
        ),
        InlineKeyboardButton(
            text="Отклонить",
            callback_data=f"rejected_application_{application.id}_{application.sending_id}",
        ),
    )

    keyboard.row(InlineKeyboardButton(text="❌ Закрыть", callback_data="close"))

    return keyboard.as_markup()
