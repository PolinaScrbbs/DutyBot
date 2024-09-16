from typing import List
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .schemes import BaseUser, UserInDB
from ..database import get_session

from . import queries as qr

router = APIRouter(prefix="/users")

@router.get("/", response_model=List[UserInDB])
async def read_users(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    users = await qr.get_users_list(session, skip, limit)
    return users

@router.get("/@{username}", response_model=BaseUser)
async def get_user_by_username(username:str, session: AsyncSession = Depends(get_session)):
    user = await qr.get_user_by_username(session, username)

    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    
    return await user.to_pydantic()