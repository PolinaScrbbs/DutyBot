from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.models import User, Role

from .models import Group


async def check_empty_groups(groups: List[Group]):
    if not groups:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="No content: groups list is empty",
        )


async def check_group_exists(group: Optional[Group]) -> Optional[HTTPException]:
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
        )


async def validate_group_access(current_user: User, group_id: Optional[int]) -> int:
    if group_id is None:
        return current_user.group_id
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access the resource",
        )
    return group_id


async def group_exists(session: AsyncSession, title: str) -> None:
    result = await session.execute(select(exists().where(Group.title == title)))
    group_exists = result.scalar()

    if group_exists:
        HTTPException(
            status.HTTP_409_CONFLICT, "A group with this title already exists"
        )
