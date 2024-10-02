import aiohttp

from config import API_URL


async def registraion(
    username: str, password: str, confirm_password: str, full_name: str
):
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.post(
            "/auth/registration",
            json={
                "username": username,
                "password": password,
                "confirm_password": confirm_password,
                "full_name": full_name,
            },
        ) as response:
            return response.status, await response.json()


async def authorization(username: str, password: str):
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.post(
            "/auth/login", data={"username": username, "password": password}
        ) as response:
            return response.status, await response.json()
