from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.utils.keyboard import InlineKeyboardBuilder

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

specializations = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Экономист", callback_data="spec_Экономист"),
            InlineKeyboardButton(
                text="Специалист по ИС", callback_data="spec_Специалист по ИС"
            ),
        ],
        [
            InlineKeyboardButton(
                text="WEB-разработчик", callback_data="spec_WEB-разработчик"
            ),
            InlineKeyboardButton(
                text="Ландшафтный дизайнер", callback_data="spec_Ландшафтный дизайнер"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Рабочий легкой промышленности",
                callback_data="spec_Рабочий легкой промышленности",
            ),
            InlineKeyboardButton(text="Парикмахер", callback_data="spec_Парикмахер"),
        ],
        [
            InlineKeyboardButton(text="Косметолог", callback_data="spec_Косметолог"),
            InlineKeyboardButton(text="Дизайнер", callback_data="spec_Дизайнер"),
        ],
        [
            InlineKeyboardButton(text="Пожарный", callback_data="spec_Пожарный"),
            InlineKeyboardButton(text="Строитель", callback_data="spec_Строитель"),
        ],
        [
            InlineKeyboardButton(
                text="BIM-специалист", callback_data="spec_BIM-специалист"
            ),
            InlineKeyboardButton(text="Банкир", callback_data="spec_Банкир"),
        ],
        [
            InlineKeyboardButton(text="Финансист", callback_data="spec_Финансист"),
            InlineKeyboardButton(text="Сварщик", callback_data="spec_Сварщик"),
        ],
        [
            InlineKeyboardButton(
                text="Пекарь-кондитер", callback_data="spec_Пекарь-кондитер"
            ),
            InlineKeyboardButton(
                text="Промышленный дизайнер мебели",
                callback_data="spec_Промышленный дизайнер мебели",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Дизайнер интерьера", callback_data="spec_Дизайнер интерьера"
            ),
            InlineKeyboardButton(text="Атомщик", callback_data="spec_Атомщик"),
        ],
        [
            InlineKeyboardButton(
                text="Общестроительный рабочий",
                callback_data="spec_Общестроительный рабочий",
            )
        ],
        [InlineKeyboardButton(text="❌", callback_data="cancel")],
    ]
)

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


async def inline_groups(groups_list):
    keyboard = InlineKeyboardBuilder()

    len_range = len(groups_list) if len(groups_list) % 2 == 0 else len(groups_list) - 1

    for j in range(0, len_range, 2):
        keyboard.row(
            InlineKeyboardButton(
                text=f"{groups_list[j].title}",
                callback_data=f"group_{groups_list[j].id}_{groups_list[j].title}",
            ),
            InlineKeyboardButton(
                text=f"{groups_list[j + 1].title}",
                callback_data=f"group_{groups_list[j + 1].id}_{groups_list[j + 1].title}",
            ),
        )

    if len(groups_list) % 2 != 0:
        keyboard.row(
            InlineKeyboardButton(
                text=f"{groups_list[-1].title}",
                callback_data=f"group_{groups_list[-1].id}_{groups_list[-1].title}",
            )
        )

    keyboard.row(InlineKeyboardButton(text="❌", callback_data="cancel"))

    return keyboard.as_markup()
