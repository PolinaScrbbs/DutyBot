import re
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .duty import router

import response as response
import keyboards as kb
import utils as ut

@router.message(lambda message: re.match(r"^Заявки\(\d+\)$", message.text))
async def admin_applications(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = user_data["token"]
    applications = user_data.get("applications")

    if not applications:
        status, applications = await response.get_applications(
            token=token, application_type="Стать старостой"
        )

        if status == 204:
            await message.answer("Список заявок пуст")
            return

        await state.update_data(applications=applications)

    await message.answer(
        "*Заявки*",
        parse_mode="Markdown",
        reply_markup=await kb.inline_applications(applications),
    )




    

