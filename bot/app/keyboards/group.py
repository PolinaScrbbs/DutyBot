from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, WebAppInfo,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import KeyboardBuilder, ReplyKeyboardBuilder, InlineKeyboardBuilder

elder_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Дежурства')],
    [KeyboardButton(text='Группа')],
    [KeyboardButton(text='Создатель', web_app=WebAppInfo(url='https://github.com/PolinaScrbbs'))]
],
                        resize_keyboard=True,
                        input_field_placeholder='Выберите пункт меню')

group_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Студенты', callback_data='students')],
    [InlineKeyboardButton(text='Заявки', callback_data='group_applications')],
    [InlineKeyboardButton(text='Настройки', callback_data='settings')],
    [InlineKeyboardButton(text='❌ Закрыть', callback_data='close')]
    # [InlineKeyboardButton(text='Удалить группу', callback_data='group_delete')]
])

async def inline_students(students):
    keyboard = InlineKeyboardBuilder()

    len_range = len(students) if len(students) % 2 == 0 else len(students) - 1

    for j in range(0, len_range, 2):
        keyboard.row(
            InlineKeyboardButton(text=f"{students[j].username}", callback_data=f"st_{students[j].id}_{students[j].username}"),
            InlineKeyboardButton(text=f"{students[j + 1].username}", callback_data=f"st_{students[j + 1].id}_{students[j + 1].username}")
        )

    if len(students) % 2 != 0:
        keyboard.row(InlineKeyboardButton(text=f"{students[-1].username}", callback_data=f"st_{students[-1].id}_{students[-1].username}"))

    keyboard.row(InlineKeyboardButton(text='❌ Закрыть', callback_data='close'))

    return keyboard.as_markup()

async def inline_student(user_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Выгнать', callback_data=f'delete_student_{user_id}'))

    return keyboard.as_markup()