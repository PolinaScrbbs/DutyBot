from typing import List
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..auth.queries import get_current_user
from ..user.models import User
from ..user import utils as ut

from .schemes import BaseGroup, GroupInDB, GroupResponse, GroupForm
from . import queries as qr

router = APIRouter(prefix="/groups")

@router.get("/", response_model=List[GroupInDB])
async def get_groups(
    skip: int = 0, 
    limit: int = 10, 
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
) -> List[GroupInDB]:
    await ut.admin_check(user)
    groups = await qr.get_groups_list(session, skip, limit)
    return groups

@router.post("/", response_model=GroupResponse)
async def post_group(
    group_data: GroupForm,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
) -> GroupResponse:
    await ut.elder_check(user)
    # group = await qr.get_group_by_title(session, group_data.title)

    # if group is not None:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="A band with that name already exists"
    #     )

    group = await qr.create_group(session, group_data, user.id)

    return GroupResponse(
        message=f'The group "{group.title}" was created by {user.username}',
        group=await group.to_pydantic()
    )

@router.get("/@{group_title}", response_model=BaseGroup)
async def get_group_by_title(
    group_title: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
) -> GroupInDB:
    await ut.admin_check(user)
    group = await qr.get_group_by_title(session, group_title)

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Group not found"
        )

    return await group.to_pydantic()

@router.get("/{group_id}", response_model=GroupInDB)
async def get_group_by_id(
    group_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
) -> GroupInDB:
    await ut.admin_check(user)
    group = await qr.get_group_by_id(session, group_id)

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Group not found"
        )

    return group

    
    