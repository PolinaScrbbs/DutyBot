from typing import Tuple

import aiohttp

from config import API_URL


async def get_specializations(token: str):
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            "/specializations", headers={"Authorization": f"Bearer {token}"}
        ) as response:
            return response.status, await response.json()


async def post_group(title: str, specialization: str, course_number: int, token: str):
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.post(
            "/groups",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": title,
                "specialization": specialization,
                "course_number": course_number,
            },
        ) as response:
            return response.status, await response.json()
        

async def get_groups(
    skip: int = 0, 
    limit: int = 10, 
    without_application: bool = False,
    token = str
) -> Tuple[int, list]:
    
    params = {
        "skip": skip,
        "limit": limit,
        "without_application": str(without_application)
    }

    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            "/groups",
            headers={"Authorization": f"Bearer {token}"},
            params=params
        ) as response:
            return response.status, await response.json()
