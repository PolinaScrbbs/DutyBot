from fastapi import HTTPException, status
from sqlalchemy.sql import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Role


async def admin_check(user: User):
    if user.role is not Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient rights to access this resource",
        )


async def elder_check(user: User):
    if user.role is Role.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient rights to access this resource",
        )
    

async def user_exists_by_username(session: AsyncSession, username: str) -> bool:
    result = await session.execute(
        select(exists().where(User.username == username))
    )

    return result.scalar()

