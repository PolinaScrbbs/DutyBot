import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from app.handlers.start import router

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print('Бот запущен')
        asyncio.run(main())
    except Exception as e:
        print(f'Бот выключен {str(e)}')