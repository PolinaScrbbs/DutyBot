from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User

async def get_users_list(
    session: AsyncSession, skip: Optional[int], limit: Optional[int]
) -> List[User]:
    
    result = await session.execute(
        select(User)
        .options(
            selectinload(User.created_group),
            selectinload(User.group),
            selectinload(User.token)
        )
        .offset(skip)
        .limit(limit)
    )

    return result.scalars().all()

async def get_user_by_username(
    session: AsyncSession, username: str
) -> User:
    
    result = await session.execute(
        select(User).where(User.username==username)
        .options(
            selectinload(User.token)
        )
    )

    return result.scalar_one_or_none()