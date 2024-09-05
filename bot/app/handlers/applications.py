import asyncio
from datetime import time
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import database.requests as rq
import app.utils as ut
from database.models import ApplicationType

from database import get_async_session
from .group import router


@router.callback_query(F.data == "grp_applications")
async def group_applications_list(callback: CallbackQuery, state: FSMContext):
    session = await get_async_session()
    data = await state.get_data()
    group = data[callback.from_user.id]["group"]

    try:
        applications = await rq.get_applications(
            session, ApplicationType.GROUP_JOIN, group.id
        )

        if not applications:
            await callback.message.edit_text("Список заявок пуст")
        else:
            await callback.message.edit_text(
                "*Заявки*",
                parse_mode="Markdown",
                reply_markup=await kb.inline_applications(applications),
            )

    except Exception as e:
        return f"{e}"

    finally:
        await session.close()


@router.message(lambda message: message.text.startswith("Заявки"))
async def admin_applications_list(message: Message, state: FSMContext):
    data = await state.get_data()
    user_data = data.get(message.from_user.id, None)
    user = user_data["user"]

    try:
        await ut.admin_check(user)

        session = await get_async_session()
        applications = await rq.get_applications(
            session, ApplicationType.BECOME_ELDER, None
        )
        await session.close()

        if not applications:
            await message.answer("Список заявок пуст")
        else:
            await message.answer(
                "*Заявки*",
                parse_mode="Markdown",
                reply_markup=await kb.inline_applications(applications),
            )

    except Exception as e:
        await message.answer(str(e))


@router.callback_query(lambda query: query.data.startswith("application_"))
async def application(callback: CallbackQuery):
    session = await get_async_session()

    callback_data_fields = callback.data.split("_")
    application_id = int(callback_data_fields[1])
    sending_id = int(callback_data_fields[2])

    application = await rq.get_application_by_id(session, application_id)
    user = await rq.get_user_by_id(session, sending_id)

    await callback.message.edit_text(
        f"Заявка @*{user.username}* ({user.surname} {user.name})",
        parse_mode="Markdown",
        reply_markup=await kb.inline_application(application),
    )

    await session.close()


@router.callback_query(lambda query: query.data.startswith("accept_application_"))
async def accept_application(callback: CallbackQuery):
    session = await get_async_session()

    callback_data_fields = callback.data.split("_")
    application_id = int(callback_data_fields[2])
    sending_id = int(callback_data_fields[3])

    try:
        application, msg = await rq.accept_application(
            session, application_id, sending_id
        )

        application_type_enum = ApplicationType(application.type)
        applications = await rq.get_applications(
            session, application_type_enum, application.group_id
        )

        await callback.message.edit_text(msg, parse_mode="Markdown")
        await asyncio.sleep(3)

        if not applications:
            await callback.message.edit_text("Список заявок пуст")
        else:
            await callback.message.edit_text(
                "*Заявки*",
                parse_mode="Markdown",
                reply_markup=await kb.inline_applications(applications),
            )

    except Exception as e:
        print(e)

    finally:
        await session.close()


@router.callback_query(lambda query: query.data.startswith("rejected_application_"))
async def rejected_application(callback: CallbackQuery):
    session = await get_async_session()

    callback_data_fields = callback.data.split("_")
    application_id = int(callback_data_fields[2])
    sending_id = int(callback_data_fields[3])

    try:
        application, msg = await rq.rejected_application(
            session, application_id, sending_id
        )

        application_type_enum = ApplicationType(application.type)
        applications = await rq.get_applications(
            session, application_type_enum, application.group_id
        )

        await callback.message.edit_text(msg, parse_mode="Markdown")
        await asyncio.sleep(3)

        if not applications:
            await callback.message.edit_text("Список заявок пуст")
        else:
            await callback.message.edit_text(
                "*Заявки*",
                parse_mode="Markdown",
                reply_markup=await kb.inline_applications(applications),
            )

    except Exception as e:
        print(e)
    finally:
        await session.close()
