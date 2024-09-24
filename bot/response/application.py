from typing import Optional, Tuple

import aiohttp

from config import API_URL

async def post_application(
    token: str,
    type: str = "Стать старостой",
    group_id: Optional[int] = None
) -> Tuple[int, dict]:
    
    async with aiohttp.ClientSession(API_URL) as session:
        async with session.post(
            "/applications",
            headers={"Authorization": f"Bearer {token}"},
            json={"application_type": type, "group_id": group_id}
        ) as response:
            return response.status, await response.json()