from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

async def admin_main(application_count: int):
    admin_main = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"Заявки({application_count})")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню",
    )

    return admin_main