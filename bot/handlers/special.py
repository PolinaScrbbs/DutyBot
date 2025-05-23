from aiogram import F, Bot, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from .. import response
from .. import keyboards as kb
from .. import utils as ut

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from ..config import config as conf

bot = Bot(conf.bot_token)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(message, user_data, False)

    if token:
        msg = (
            f"👋 Привет, @{message.from_user.username}! Рады снова видеть тебя!\n"
            "Выбери нужный раздел в меню ниже 🔍"
        )

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
                keyboard = kb.ungroup_main
                if user["group_id"] is not None:
                    try:
                        group = await response.get_group(token)
                        user_data["group"] = group
                        await state.update_data(user_data)
                        keyboard = kb.student_main
                    except Exception:
                        user["group_id"] = None
                        await ut.clear_user_data(state, token, user, None)

            case "Староста":
                keyboard = kb.ungroup_main
                if user["group_id"] is not None:
                    group = await response.get_group(token)
                    user_data["group"] = group
                    await state.update_data(user_data)
                    keyboard = kb.elder_main
    else:
        msg = "👋 Добро пожаловать! Пожалуйста, выбери пункт меню ниже, чтобы начать 🔍"
        keyboard = kb.start

    await message.answer(text=msg, parse_mode="Markdown", reply_markup=keyboard)


@router.message(Command("profile"))
async def profile(message: Message, state: FSMContext):
    user_data = await state.get_data()

    try:
        token = await ut.get_user_token(message, user_data)

        if token:
            web_app_url = f"{conf.ngrok_url}/profile?username={message.from_user.username}&token={token}"

            inline_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="👤 Перейти в профиль",
                            web_app=WebAppInfo(url=web_app_url),
                        )
                    ]
                ]
            )

            await message.answer(
                "Для просмотра вашего профиля нажмите на кнопку ниже 👇",
                reply_markup=inline_keyboard,
            )
    except KeyError:
        await message.answer(
            "❗️ Профиль недоступен. Пожалуйста, авторизуйтесь, чтобы продолжить.",
            reply_markup=kb.start,
        )


@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    try:
        token = await ut.get_user_token(callback, user_data)
        user = user_data.get("user")
        group = user_data.get("group")
        await state.clear()
        await state.update_data({"token": token, "user": user, "group": group})
    except Exception:
        await state.clear()

    await callback.message.edit_text(
        "❌ Действие отменено. Если что — всегда можно начать заново!"
    )


@router.callback_query(F.data == "close")
async def close(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    try:
        token = await ut.get_user_token(callback, user_data)
        user = user_data.get("user")
        group = user_data.get("group")
        await state.clear()
        await state.update_data({"token": token, "user": user, "group": group})
    except KeyError:
        await state.clear()

    await callback.message.edit_text(
        "✅ Окно успешно закрыто. Если понадобится — обращайтесь! 👋"
    )
