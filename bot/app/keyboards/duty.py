from typing import Optional
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

attendants = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔄', callback_data='remapFirst'), InlineKeyboardButton(text='🔄', callback_data='remapSecond')],
    [InlineKeyboardButton(text='✅Назначить', callback_data='attendants_assign')], 
    [InlineKeyboardButton(text='❌Отмена', callback_data='cancel')]
])