from typing import Tuple
import aiohttp

from ..config import config as conf


async def get_user_by_username(username: str, token: str) -> Tuple[int, dict]:
    async with aiohttp.ClientSession(conf.api_url) as session:
        async with session.get(
            f"/user/@{username}", headers={"Authorization": f"Bearer {token}"}
        ) as response:
            return response.status, await response.json()


async def get_user_by_id(user_id: int, token: str) -> Tuple[int, dict]:
    async with aiohttp.ClientSession(conf.api_url) as session:
        async with session.get(
            f"/user/{user_id}", headers={"Authorization": f"Bearer {token}"}
        ) as response:
            return response.status, await response.json()
