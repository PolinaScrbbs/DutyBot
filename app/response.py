import sys
import os
from typing import Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aiohttp
from config import API_URL


async def get_user(username: str, token: str) -> Tuple[int, dict]:
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            f"/user/@{username}", headers={"Authorization": f"Bearer {token}"}
        ) as response:
            status = response.status
            if status == 200:
                return status, await response.json()


async def get_groups(token: str) -> Tuple[int, dict]:
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            "/groups", headers={"Authorization": f"Bearer {token}"}
        ) as response:
            return response.status, await response.json()


async def get_group(token: str) -> Tuple[int, dict]:
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            "/group", headers={"Authorization": f"Bearer {token}"}
        ) as response:
            return response.status, await response.json()


async def get_students(token: str) -> Tuple[int, dict]:
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            "/group/students", headers={"Authorization": f"Bearer {token}"}
        ) as response:
            return response.status, await response.json()


async def get_duties(token: str) -> Tuple[int, dict]:
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            "/duties", headers={"Authorization": f"Bearer {token}"}
        ) as response:
            return response.status, await response.json()
