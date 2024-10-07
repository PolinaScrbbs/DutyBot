from aiogram import F, Bot, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

import response as response
import keyboards as kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
router = Router()

async def set_user_profile_button(bot, chat_id, username, token):
    await bot.set_chat_menu_button(
        menu_button={
            "type": "web_app",
            "text": "Профиль",
            "web_app": {
                "url": f""
            }
        },
        chat_id=chat_id 
    )
                
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = user_data.get("token", None)

    if token:
        msg = (
            f"С возвращением, @{message.from_user.username}👋 \nВыбери пункт из меню🔍"
        )

        status, user = await response.get_user_by_username(
            message.from_user.username, token
        )

        # await set_user_profile_button(
        #     bot=bot, 
        #     chat_id=message.chat.id, 
        #     username=message.from_user.username, 
        #     token=token
        # )

        user_data["user"] = user
        await state.update_data(user_data)

        if user["role"] == "Администратор":
            status, applications = await response.get_applications(
                token=token, application_type="Стать старостой"
            )
            applications_count = 0
            if status == 200:
                applications_count = len(applications)
            keyboard = await kb.admin_main(applications_count)
            user_data["applications"] = applications
            await state.update_data(user_data)

        elif user["group_id"] is not None:
            group = await response.get_group(token)
            user_data["group"] = group
            await state.update_data(user_data)

            if user["role"] == "Студент":
                pass
            else:
                keyboard = kb.elder_main
        else:
            keyboard = kb.ungroup_main

    else:
        msg = "Привет👋\nВыбери пункт из меню🔍"
        keyboard = kb.start

    await message.answer(text=msg, parse_mode="Markdown", reply_markup=keyboard)

@router.message(Command("profile"))
async def profile(message: Message, state: FSMContext):
    user_data = await state.get_data()
    web_app_url = f"https://48d4-176-194-227-178.ngrok-free.app/profile?username={message.from_user.username}&token={user_data['token']}"

    # Создаем инлайн-кнопку
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть профиль", web_app=WebAppInfo(url=web_app_url))]
        ]
    )

    await message.answer("Откройте профиль, нажав на кнопку ниже:", reply_markup=inline_keyboard)

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
