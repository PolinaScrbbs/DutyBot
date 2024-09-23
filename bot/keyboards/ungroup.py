from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
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
