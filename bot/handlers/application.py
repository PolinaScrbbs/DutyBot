import asyncio

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .admin import router, admin_applications

from .. import response
from .. import keyboards as kb
from .. import utils as ut


@router.callback_query(F.data == "grp_applications")
async def group_applications_list(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)

    if token:
        user = user_data["user"]

        status, applications = await response.get_applications(
            token=token,
            application_type="На вступление в группу",
            group_id=f"{user['group_id']}",
        )

        if status == 204:
            await callback.message.edit_text(
                "📭 Список заявок пуст. Пока что никто не подал заявку."
            )

        else:
            await callback.message.edit_text(
                "📋 *Текущие заявки*",
                parse_mode="Markdown",
                reply_markup=await kb.inline_applications(applications),
            )


@router.callback_query(lambda query: query.data.startswith("application_"))
async def application(callback: CallbackQuery, state: FSMContext):
    callback_data_fields = callback.data.split("_")
    application_id = int(callback_data_fields[1])

    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)

    if token:
        status, application_dict = await response.get_application(token, application_id)

        sending = application_dict["sending"]
        first_name, last_name = sending["full_name"].split()[:2]

        await callback.message.edit_text(
            f"📄 Заявка пользователя @*{sending['username']}* ({first_name} {last_name})",
            parse_mode="Markdown",
            reply_markup=await kb.inline_application(application_dict),
        )


@router.callback_query(lambda query: query.data.startswith("update_application_"))
async def update_application(callback: CallbackQuery, state: FSMContext):
    callback_data_fields = callback.data.split("_")
    application_id = int(callback_data_fields[2])
    update_status = callback_data_fields[3]

    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)

    if token:
        await response.put_application(token, application_id, update_status)

        msg = "⚠️ Заявка отклонена"
        if update_status == "Принят":
            msg = "✅ Заявка успешно принята"

        await callback.message.edit_text(msg)

        user = user_data["user"]
        if user["role"] == "Администратор":
            await ut.clear_user_data(state, token, user)
            await asyncio.sleep(3)
            await admin_applications(callback.message, state)
        else:
            await asyncio.sleep(3)
            await group_applications_list(callback, state)
