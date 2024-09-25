from typing import Optional, Tuple

import aiohttp

from config import API_URL


async def post_application(
    token: str, type: str = "Стать старостой", group_id: Optional[int] = None
) -> Tuple[int, dict]:

    async with aiohttp.ClientSession(API_URL) as session:
        async with session.post(
            "/applications",
            headers={"Authorization": f"Bearer {token}"},
            json={"application_type": type, "group_id": group_id},
        ) as response:
            return response.status, await response.json()


async def get_applications(
    token: str,
    skip: int = 0,
    limit: int = 10,
    application_type: str = "Стать старостой",
    group_id: Optional[int] = None,
) -> Tuple[int, dict]:

    params = {
        "skip": skip,
        "limit": limit,
        "application_type": application_type,
        "group_id": group_id,
    }

    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            "/applications", headers={"Authorization": f"Bearer {token}"}, params=params
        ) as response:
            return response.status, await response.json()
