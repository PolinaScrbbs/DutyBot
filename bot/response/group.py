import aiohttp

from config import API_URL


async def get_specializations(token: str):
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.get(
            f"/specializations", headers={"Authorization": f"Bearer {token}"}
        ) as response:
            return response.status, await response.json()


async def post_group(title: str, specialization: str, course_number: int, token: str):
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.post(
            f"/groups",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": title,
                "specialization": specialization,
                "course_number": course_number,
            },
        ) as response:
            return response.status, await response.json()
