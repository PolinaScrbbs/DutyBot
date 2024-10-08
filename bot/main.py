import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.special import bot
from handlers.admin import router
from handlers.group import group_menu

@router.callback_query(F.data == "back")
async def back(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user_data = await state.get_data()
    back_in_data = user_data["back_in"]

    fun_dict = {
        "group_menu": group_menu,
    }

    if back_in_data and back_in_data["function"] in fun_dict:
        menu_function = fun_dict[back_in_data["function"]]
        params = back_in_data.get("params", {})
        await menu_function(**params)
    else:
        print("Функция не найдена или back_in_data пуст.")


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    try:
        print("Бот запущен")
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        print("Бот выключен вручную")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
