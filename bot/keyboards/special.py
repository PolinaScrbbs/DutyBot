from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

start = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Авторизация"), KeyboardButton(text="Регистрация")],
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

cancel = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="❌", callback_data="cancel")]]
)


def get_pagination_kb(tag: str, offset: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀ Назад", callback_data=f"{tag}:prev:{offset}"
                ),
                InlineKeyboardButton(
                    text="Вперёд ▶", callback_data=f"{tag}:next:{offset}"
                ),
            ],
            [InlineKeyboardButton(text="❌ Закрыть", callback_data=f"{tag}:close")],
        ]
    )
