from typing import List
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .schemes import HiddenUser, BaseUser, UserInDB
from . import utils as ut
from ..database import get_session
from ..auth.queries import get_current_user

from . import queries as qr

router = APIRouter()


@router.get("/users", response_model=List[UserInDB])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    await ut.admin_check(user)
    users = await qr.get_users_list(session, skip, limit)
    return users


@router.get("/user/@{username}", response_model=HiddenUser)
async def get_user_by_username(
    username: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = await qr.get_user_by_username(session, username)

    return await HiddenUser(
        id=user.id, role=user.role, username=user.username, full_name=user.full_name
    )


@router.get("/user/{id}", response_model=BaseUser)
async def get_user_by_id(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await ut.admin_check(current_user)
    user = await qr.get_user_by_id(session, id)

    return await user.to_pydantic()
