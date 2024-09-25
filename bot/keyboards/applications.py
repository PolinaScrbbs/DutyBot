from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def inline_applications(applications):
    keyboard = InlineKeyboardBuilder()

    len_range = (
        len(applications) if len(applications) % 2 == 0 else len(applications) - 1
    )

    for j in range(0, len_range, 2):
        first_name, last_name = applications[j]["sending"]["full_name"].split()[:2]
        second_first_name, second_last_name = applications[j + 1]["sending"][
            "full_name"
        ].split()[:2]

        keyboard.row(
            InlineKeyboardButton(
                text=f"@{applications[j]['sending']['username']} ({first_name} {last_name})",
                callback_data=f"application_{applications[j]['id']}_{applications[j]['sending']['id']}",
            ),
            InlineKeyboardButton(
                text=f"@{applications[j + 1]['sending']['username']} ({second_first_name} {second_last_name})",
                callback_data=f"application_{applications[j + 1]['id']}_{applications[j + 1]['sending']['id']}",
            ),
        )

    if len(applications) % 2 != 0:
        first_name, last_name = applications[-1]["sending"]["full_name"].split()[:2]

        keyboard.row(
            InlineKeyboardButton(
                text=f"@{applications[-1]['sending']['username']} ({first_name} {last_name})",
                callback_data=f"application_{applications[-1]['id']}_{applications[-1]['sending']['id']}",
            )
        )

    keyboard.row(InlineKeyboardButton(text="Назад", callback_data="back"))

    return keyboard.as_markup()


async def inline_application(application):
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(
            text="Принять",
            callback_data=f"update_application_{application['id']}_Принят",
        ),
        InlineKeyboardButton(
            text="Отклонить",
            callback_data=f"update_application_{application['id']}_Отклонен",
        ),
    )

    keyboard.row(InlineKeyboardButton(text="❌ Закрыть", callback_data="close"))

    return keyboard.as_markup()
