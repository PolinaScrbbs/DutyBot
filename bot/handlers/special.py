from aiogram import F, Bot, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from .. import response
from .. import keyboards as kb
#from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from ..config import config as conf

bot = Bot(conf.bot_token)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = user_data.get("token", None)

    if token:
        msg = f"С возвращением, @{message.from_user.username}👋 \nВыбери пункт из меню🔍"

        status, user = await response.get_user_by_username(
            message.from_user.username, token
        )

        user_data["user"] = user
        await state.update_data(user_data)

        match user["role"]:
            case "Администратор":
                status, applications = await response.get_applications(
                    token=token, application_type="Стать старостой"
                )
                applications_count = len(applications) if status == 200 else 0
                keyboard = await kb.admin_main(applications_count)
                user_data["applications"] = applications
                await state.update_data(user_data)

            case "Студент":
                if user["group_id"] is not None:
                    group = await response.get_group(token)
                    user_data["group"] = group
                    await state.update_data(user_data)
                    keyboard = kb.student_main
                else:
                    keyboard = kb.ungroup_main

            case _:
                if user["group_id"] is not None:
                    group = await response.get_group(token)
                    user_data["group"] = group
                    await state.update_data(user_data)
                    keyboard = kb.elder_main
                else:
                    keyboard = kb.ungroup_main
    else:
        msg = "Привет👋\nВыбери пункт из меню🔍"
        keyboard = kb.start

    await message.answer(text=msg, parse_mode="Markdown", reply_markup=keyboard)



# @router.message(Command("profile"))
# async def profile(message: Message, state: FSMContext):
#     user_data = await state.get_data()
#     token = user_data["token"]
#     print(message.from_user.username, token)
#     web_app_url = (
#         f"{NGROK_URL}profile?username={message.from_user.username}&token={token}"
#     )
#
#     inline_keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text="Открыть профиль", web_app=WebAppInfo(url=web_app_url)
#                 )
#             ]
#         ]
#     )
#
#     await message.answer(
#         "Откройте профиль, нажав на кнопку ниже:", reply_markup=inline_keyboard
#     )


@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    try:
        token = user_data["token"]
        user = user_data["user"]
        group = user_data["group"]
        await state.clear()
        await state.update_data({"token": token, "user": user, "group": group})
    except:
        await state.clear()

    await callback.message.edit_text("✅ Отменено")


@router.callback_query(F.data == "close")
async def close(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    try:
        token = user_data["token"]
        user = user_data["user"]
        group = user_data["group"]
        await state.clear()
        await state.update_data({"token": token, "user": user, "group": group})
    except:
        await state.clear()

    await callback.message.edit_text("✅ Закрыто")
