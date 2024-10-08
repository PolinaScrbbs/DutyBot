from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from ..group.models import Group


async def get_users_list(
    session: AsyncSession, skip: Optional[int], limit: Optional[int]
) -> List[User]:

    result = await session.execute(
        select(User)
        .options(
            selectinload(User.created_group).load_only(
                Group.title, Group.specialization, Group.course_number, Group.creator_id
            ),
            selectinload(User.group).load_only(
                Group.title, Group.specialization, Group.course_number, Group.creator_id
            ),
            selectinload(User.token),
        )
        .offset(skip)
        .limit(limit)
    )

    return result.scalars().all()


async def get_user_by_username(session: AsyncSession, username: str) -> User:

    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


async def get_user_by_id(session: AsyncSession, id: int) -> User:
    result = await session.execute(select(User).where(User.id == id))

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    return user
