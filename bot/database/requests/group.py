from typing import List, Optional
from enum import Enum

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from ..models.users import Specialization, Group, Application
from .user import get_user

async def create_group(session: AsyncSession, title: str, specialization: Specialization, course_number: int, creator_username: str) -> Group:
    user = await get_user(session, creator_username)

    group = Group(
        title = title,
        specialization = specialization,
        course_number = course_number,
        creator_id = user.id
    )

    try:
        session.add(group)
        await session.commit()
        return group
    
    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        await session.close()

async def get_groups(session: AsyncSession) -> List[Group]:
    try:
        result = await session.execute(
            select(Group)
        )

        groups = result.scalars().all()

        return groups
    
    except Exception as e:
        print(f"Error: {e}")
        return []
    
async def get_group(session: AsyncSession, id: int) -> Group:
    try:
        result = await session.execute(
            select(Group).where(Group.id == id)
        )
        group = result.scalars().one_or_none()

        return group if group else None
    
    except Exception as e:
        print(f"Error: {e}")
        return None

async def get_groups_without_application_from_user(session: AsyncSession, user_id) -> List[Group]:
    try:
        groups = await get_groups(session)

        groups_with_application = await session.execute(
            select(Application.group_id).where(Application.sending_id == user_id)
            )
        groups_with_application_ids = groups_with_application.scalars().all()

        groups_without_application = [group for group in groups if group.id not in groups_with_application_ids]

        return groups_without_application
    
    except Exception as e:
        print(f"Error: {e}")
        return []
    
    finally:
        await session.close()

async def get_specialization(text: str) -> Specialization:
    for spec in Specialization:
        if spec.value == text:
            return spec
    raise ValueError(f"Specialization с текстом '{text}' не найдена.")