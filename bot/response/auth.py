import aiohttp
from aiogram import Bot

from config import API_URL

from utils import get_user_avatar


async def registraion(
    bot: Bot, user_id: int, username: str, password: str, confirm_password: str, full_name: str
):  
    avatar_url = await get_user_avatar(bot, user_id)

    async with aiohttp.ClientSession(API_URL) as session:
        async with session.post(
            "/auth/registration",
            json={
                "username": username,
                "password": password,
                "confirm_password": confirm_password,
                "full_name": full_name,
                "avatar_url": avatar_url
            },
        ) as response:
            return response.status, await response.json()


async def authorization(username: str, password: str):
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.post(
            "/auth/login", data={"username": username, "password": password}
        ) as response:
            return response.status, await response.json()
