from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.models import User

from .models import Group, Specialization
from .schemes import BaseGroup, GroupInDB

async def get_groups_list(
    session: AsyncSession, 
    skip: Optional[int], 
    limit: Optional[int]
) -> List[GroupInDB]:
    
    result = await session.execute(
        select(Group)
        .options(
            selectinload(Group.creator)
                .load_only(
                    User.role,
                    User.username,
                    User.full_name
                ),
            selectinload(Group.students)
        )
        .offset(skip)
        .limit(limit)
    )

    return result.scalars().all()

async def create_group(session: AsyncSession, group_create: BaseGroup) -> BaseGroup:
    group = Group(
        title = group_create.title,
        specialization = Specialization(group_create.specialization),
        course_number = group_create.course_number,
        creator_id = group_create.creator_id
    )

    session.add(group)
    await session.commit()

    return group

async def get_group_by_id(session: AsyncSession, id: int) -> Group:
    result = await session.execute(
        select(Group).where(Group.id==id)
        .options(
            selectinload(Group.creator),
            selectinload(Group.students)
        )
    )

    return result.scalar_one_or_none()


async def get_group_by_title(session: AsyncSession, title: str) -> Group:
    result = await session.execute(
        select(Group).where(Group.title==title)
        .options(
            selectinload(Group.creator),
            selectinload(Group.students)
        )
    )

    return result.scalar_one_or_none()