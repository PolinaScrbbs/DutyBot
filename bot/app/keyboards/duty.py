from typing import List, Optional
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, WebAppInfo,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import KeyboardBuilder, ReplyKeyboardBuilder, InlineKeyboardBuilder

duty_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Назначить дежурных')],
    [KeyboardButton(text='Список дежурств'), KeyboardButton(text='Количество дежурств')],
    [KeyboardButton(text='Создатель', web_app=WebAppInfo(url='https://github.com/PolinaScrbbs'))]
],
                        resize_keyboard=True,
                        input_field_placeholder='Выберите пункт меню')

async def attendants(attendant_1_fullname: str, attendant_2_fullname: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text=f'🔄 {attendant_1_fullname}', callback_data='replace_attendant_0'),
        InlineKeyboardButton(text=f'🔄 {attendant_2_fullname}', callback_data='replace_attendant_1')
    )
    keyboard.row(InlineKeyboardButton(text='✅Назначить дежурных', callback_data='attendants_assign'))
    keyboard.row(InlineKeyboardButton(text='❌Отмена', callback_data='cancel'))

    return keyboard.as_markup()