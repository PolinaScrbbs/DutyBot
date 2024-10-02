import json
from typing import List, Tuple

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


async def get_attendants(token: str, missed_student_id: List[int]) -> Tuple[int, dict]:
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            "/attendants",
            json=missed_student_id,
            headers={"Authorization": f"Bearer {token}"},
        ) as response:
            return response.status, await response.json()


async def post_duty(token: str, students_id: List[int]) -> int:
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.post(
            "/duties", json=students_id, headers={"Authorization": f"Bearer {token}"}
        ) as response:
            return response.status
