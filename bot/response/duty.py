from typing import Optional, Tuple

import aiohttp

from config import API_URL


async def get_duties(token: str) -> Tuple[int, dict]:

    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            "/duties", headers={"Authorization": f"Bearer {token}"}
        ) as response:
            status = response.status
            if status == 204:
                return status, None

            return status, await response.json()
