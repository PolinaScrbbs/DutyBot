import re
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .group import router

from .. import response
from .. import keyboards as kb
from ..utils import get_user_token


@router.message(lambda message: re.match(r"^Заявки\(\d+\)$", message.text))
async def admin_applications(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = await get_user_token(message, user_data)

    if token:
        applications = user_data.get("applications")

        if not applications:
            status, applications = await response.get_applications(
                token=token, application_type="Стать старостой"
            )

            match status:
                case 403:
                    await message.answer(
                        "У вас нет прав на просмотр заявок",
                    )
                case 204:
                    await message.answer(
                        "Список заявок пуст",
                    )
                case 200:
                    await state.update_data(applications=applications)
                case _:
                    await message.answer(
                        "Произошла ошибка при получении заявок",
                    )
        else:
            await message.answer(
                "*Заявки*",
                parse_mode="Markdown",
                reply_markup=await kb.inline_applications(applications),
            )
