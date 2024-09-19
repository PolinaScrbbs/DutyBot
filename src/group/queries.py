from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.models import User
from ..user.queries import get_user_by_id

from .models import Group, Specialization
from .schemes import BaseGroup, GroupInDB


async def get_groups_list(
    session: AsyncSession, skip: Optional[int], limit: Optional[int]
) -> List[GroupInDB]:

    result = await session.execute(
        select(Group)
        .options(
            selectinload(Group.creator).load_only(
                User.role, User.username, User.full_name
            ),
            selectinload(Group.students),
        )
        .offset(skip)
        .limit(limit)
    )

    return result.scalars().all()


async def create_group(
    session: AsyncSession, group_create: BaseGroup, creator_id: int
) -> BaseGroup:

    group = Group(
        title=group_create.title,
        specialization=Specialization(group_create.specialization),
        course_number=group_create.course_number,
        creator_id=creator_id,
    )

    user = await get_user_by_id(session, creator_id)

    session.add(group)
    user.group_id = creator_id

    await session.commit()

    return group


async def get_group_by_id(session: AsyncSession, id: int) -> Group:
    result = await session.execute(
        select(Group)
        .where(Group.id == id)
        .options(selectinload(Group.creator), selectinload(Group.students))
    )

    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Group not found")

    return group


async def get_group_by_title(session: AsyncSession, title: str) -> Group:
    result = await session.execute(
        select(Group)
        .where(Group.title == title)
        .options(selectinload(Group.creator), selectinload(Group.students))
    )

    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Group not found")

    return group
