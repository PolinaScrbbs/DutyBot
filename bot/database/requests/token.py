from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.users import Token


async def get_user_token(session: AsyncSession, user_id: int) -> Token:
    try:
        result = await session.execute(select(Token).where(Token.user_id == user_id))

        token = result.scalar()
        return token

    except Exception as e:
        print(f"Error: {e}")
        return None


async def auth_check(session: AsyncSession, user_id: int) -> bool:
    token = await get_user_token(session, user_id)
    res = True

    if token == None:
        res = False

    return res
