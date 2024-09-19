from typing import List
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..auth.queries import get_current_user
from ..user.models import User
from ..user import utils as ut

from .models import Specialization
from .schemes import BaseGroup, GroupInDB, GroupResponse, GroupForm
from . import queries as qr
from .validators import GroupValidator

router = APIRouter(prefix="/groups")


@router.get("/", response_model=List[GroupInDB])
async def get_groups(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> List[GroupInDB]:
    await ut.admin_check(user)
    groups = await qr.get_groups_list(session, skip, limit)
    return groups


@router.post("/", response_model=GroupResponse)
async def post_group(
    group_data: GroupForm,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> GroupResponse:
    await ut.elder_check(user)

    if user.group_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A group with this title already exists for the current user.",
        )

    validator = GroupValidator(
        group_data.title,
        group_data.specialization,
        group_data.course_number,
        [spec.value for spec in Specialization],
        session,
    )
    await validator.validate()

    group = await qr.create_group(session, group_data, user.id)

    return GroupResponse(
        message=f'The group "{group.title}" was created by {user.username}',
        group=await group.to_pydantic(),
    )


@router.get("/@{group_title}", response_model=BaseGroup)
async def get_group_by_title(
    group_title: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> GroupInDB:
    await ut.admin_check(user)
    group = await qr.get_group_by_title(session, group_title)

    return await group.to_pydantic()


@router.get("/{group_id}", response_model=GroupInDB)
async def get_group_by_id(
    group_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> GroupInDB:
    await ut.admin_check(user)
    group = await qr.get_group_by_id(session, group_id)

    return group
