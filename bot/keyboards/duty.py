from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


duty_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Назначить дежурных")],
        [
            KeyboardButton(text="Список дежурств"),
            KeyboardButton(text="Количество дежурств"),
        ],
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

remap = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄", callback_data="remap_0"),
            InlineKeyboardButton(text="🔄", callback_data="remap_1"),
        ],
        [InlineKeyboardButton(text="✅Назначить", callback_data="assign")],
        [InlineKeyboardButton(text="❌Отмена", callback_data="cancel")],
    ],
    row_width=1,
)
