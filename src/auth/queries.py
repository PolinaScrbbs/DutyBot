from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .schemes import UserCreate

async def registration_user(
    session: AsyncSession, user_create: UserCreate
) -> User:
    
    user = User(
        username=user_create.username,
        full_name=user_create.full_name
    )
    user.set_password(user_create.password)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user

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

    
            