from typing import Dict, List

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
)

ungroup_main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Вступить в группу"),
            KeyboardButton(text="Создать группу"),
        ],
        [KeyboardButton(text="Стать старостой")],
        [
            KeyboardButton(
                text="Создатель",
                web_app=WebAppInfo(url="https://github.com/PolinaScrbbs"),
            )
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню",
)


async def create_specializations_keyboard(
    specializations: List[str],
) -> InlineKeyboardBuilder:

    keyboard = InlineKeyboardBuilder()

    len_range = (
        len(specializations)
        if len(specializations) % 2 == 0
        else len(specializations) - 1
    )
    for j in range(0, len_range, 2):
        keyboard.row(
            InlineKeyboardButton(
                text=specializations[j], callback_data=f"spec_{specializations[j]}"
            ),
            InlineKeyboardButton(
                text=specializations[j + 1],
                callback_data=f"spec_{specializations[j+1]}",
            ),
        )

    if len(specializations) % 2 != 0:
        keyboard.row(
            InlineKeyboardButton(
                text=specializations[-1], callback_data=f"spec_{specializations[-1]}"
            )
        )

    keyboard.row(InlineKeyboardButton(text="❌", callback_data="cancel"))

    return keyboard.as_markup()


course_number = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="1 курс", callback_data="course_number_1"),
            InlineKeyboardButton(text="2 курс", callback_data="course_number_2"),
            InlineKeyboardButton(text="3 курс", callback_data="course_number_3"),
            InlineKeyboardButton(text="4 курс", callback_data="course_number_4"),
        ]
    ]
)
