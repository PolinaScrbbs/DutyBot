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

async def create_group(session: AsyncSession, group_create: BaseGroup):
    group = Group(
        title = group_create.title,
        specialization = Specialization(group_create.specialization),
        course_number = group_create.course_number,
        creator_id = group_create.creator_id
    )

    session.add(group)
    await session.commit()

    return group