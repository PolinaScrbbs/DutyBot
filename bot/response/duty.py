from typing import List, Optional, Tuple

import aiohttp

from ..config import config as conf


async def get_duties(
    token: str, limit: int = 10, offset: int = 0
) -> Tuple[int, Optional[dict]]:
    params = {"limit": limit, "offset": offset}

    async with aiohttp.ClientSession(conf.api_url) as session:
        async with session.get(
            "/duties", headers={"Authorization": f"Bearer {token}"}, params=params
        ) as response:
            status = response.status
            if status == 204:
                return status, None

            return status, await response.json()


async def get_attendants(token: str, missed_student_id: List[int]) -> Tuple[int, dict]:
    async with aiohttp.ClientSession(conf.api_url) as session:
        async with session.get(
            "/attendants",
            json=missed_student_id,
            headers={"Authorization": f"Bearer {token}"},
        ) as response:
            if response.status == 204:
                return response.status, {}
            return response.status, await response.json()


async def get_current_attendants(token: str) -> Tuple[int, dict]:
    async with aiohttp.ClientSession(conf.api_url) as session:
        async with session.get(
            "/current_attendants",
            headers={"Authorization": f"Bearer {token}"},
        ) as response:
            if response.status == 204:
                return response.status, {}
            if response.status == 200:
                json = await response.json()
                return response.status, json["attendants"]


async def post_duty(token: str, students_id: List[int]) -> int:
    async with aiohttp.ClientSession(conf.api_url) as session:
        async with session.post(
            "/duties", json=students_id, headers={"Authorization": f"Bearer {token}"}
        ) as response:
            return response.status
