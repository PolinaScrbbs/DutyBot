from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
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
