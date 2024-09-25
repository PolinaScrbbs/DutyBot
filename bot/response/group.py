from typing import List, Tuple

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
    skip: int = 0, limit: int = 10, without_application: bool = False, token=str
) -> Tuple[int, list]:

    params = {
        "skip": skip,
        "limit": limit,
        "without_application": str(without_application),
    }

    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            "/groups", headers={"Authorization": f"Bearer {token}"}, params=params
        ) as response:
            return response.status, await response.json()


async def get_group(token: str) -> Tuple[int, dict]:

    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            "/group",
            headers={"Authorization": f"Bearer {token}"},
        ) as response:
            return response.status, await response.json()


async def get_students(token: str) -> Tuple[int, List[dict]]:

    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            "/group/students",
            headers={"Authorization": f"Bearer {token}"},
        ) as response:
            status = response.status
            if status == 204:
                return status, None

            return status, await response.json()


async def get_student(student_id: int, token: str) -> Tuple[int, dict]:

    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            f"/group/student/{student_id}",
            headers={"Authorization": f"Bearer {token}"},
        ) as response:
            return response.status, await response.json()


async def kick_student(student_id: int, token: str) -> Tuple[int, str]:

    async with aiohttp.ClientSession(API_URL) as session:
        async with session.delete(
            f"/group/kick/{student_id}",
            headers={"Authorization": f"Bearer {token}"},
        ) as response:
            return response.status, await response.text()
