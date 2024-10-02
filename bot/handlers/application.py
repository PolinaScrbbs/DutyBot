import asyncio

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .group import router

import response as response
import keyboards as kb


@router.callback_query(F.data == "grp_applications")
async def group_applications_list(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = user_data["token"]
    user = user_data["user"]

    status, applications = await response.get_applications(
        token=token,
        application_type="На вступление в группу",
        group_id=f"{user['group_id']}",
    )

    if status == 204:
        await callback.message.edit_text("Список заявок пуст")

    else:
        await callback.message.edit_text(
            "*Заявки*",
            parse_mode="Markdown",
            reply_markup=await kb.inline_applications(applications),
        )


@router.callback_query(lambda query: query.data.startswith("application_"))
async def application(callback: CallbackQuery, state: FSMContext):
    callback_data_fields = callback.data.split("_")
    application_id = int(callback_data_fields[1])

    user_data = await state.get_data()
    token = user_data["token"]

    status, application = await response.get_application(token, application_id)

    sending = application["sending"]
    first_name, last_name = sending["full_name"].split()[:2]

    await callback.message.edit_text(
        f"Заявка @*{sending['username']}* ({first_name} {last_name})",
        parse_mode="Markdown",
        reply_markup=await kb.inline_application(application),
    )


@router.callback_query(lambda query: query.data.startswith("update_application_"))
async def update_application(callback: CallbackQuery, state: FSMContext):
    callback_data_fields = callback.data.split("_")
    application_id = int(callback_data_fields[2])
    update_status = callback_data_fields[3]

    user_data = await state.get_data()
    token = user_data["token"]

    await response.put_application(token, application_id, update_status)

    msg = "✅ Заявка отклонена"
    if update_status == "Принять":
        msg = "✅ Заявка принята"

    await callback.message.edit_text(msg)

    await asyncio.sleep(3)
    await group_applications_list(callback, state)
