from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..auth.queries import get_current_user
from ..user.models import User
from ..user import utils as ut

from .schemes import BaseGroup, GroupInDB, GroupResponse
from .queries import get_groups_list, create_group

router = APIRouter(prefix="/groups")

@router.get("/", response_model=List[GroupInDB])
async def get_groups(
    skip: int = 0, 
    limit: int = 10, 
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
) -> List[GroupInDB]:
    await ut.admin_check(user)
    groups = await get_groups_list(session, skip, limit)
    return groups

@router.post("/", response_model=GroupResponse)
async def post_group(
    group_data: BaseGroup,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
) -> GroupResponse:
    await ut.elder_check(user)
    group = await create_group(session, group_data)

    return GroupResponse(
        message=f'The group "{group.title}" was created by {user.username}',
        group=await group.to_pydantic()
    )
    