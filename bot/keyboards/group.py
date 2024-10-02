from typing import Optional
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.utils.keyboard import InlineKeyboardBuilder

elder_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Дежурства")],
        [KeyboardButton(text="Группа")],
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


async def group_menu(application_count: Optional[int]):
    group_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Студенты", callback_data="students")],
            [
                InlineKeyboardButton(
                    text=f"Заявки {f'({application_count})' if application_count > 0 else ''}",
                    callback_data="grp_applications",
                )
            ],
            [InlineKeyboardButton(text="Настройки", callback_data="settings")],
            [InlineKeyboardButton(text="❌ Закрыть", callback_data="close")],
            # [InlineKeyboardButton(text='Удалить группу', callback_data='group_delete')]
        ]
    )

    return group_menu


async def inline_students(students):
    keyboard = InlineKeyboardBuilder()

    len_range = len(students) if len(students) % 2 == 0 else len(students) - 1

    for j in range(0, len_range, 2):
        keyboard.row(
            InlineKeyboardButton(
                text=f"{students[j]['student']['username']}",
                callback_data=f"st_{students[j]['student']['username']}",
            ),
            InlineKeyboardButton(
                text=f"{students[j + 1]['student']['username']}",
                callback_data=f"st_{students[j + 1]['student']['username']}",
            ),
        )

    if len(students) % 2 != 0:
        keyboard.row(
            InlineKeyboardButton(
                text=f"{students[-1]['student']['username']}",
                callback_data=f"st_{students[-1]['student']['username']}",
            )
        )

    keyboard.row(InlineKeyboardButton(text="Назад", callback_data="back"))

    return keyboard.as_markup()


async def inline_student(student: dict):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Выгнать", callback_data=f"kick_{student['id']}")
    )

    return keyboard.as_markup()
