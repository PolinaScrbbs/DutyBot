from typing import List
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .schemes import BaseUser, UserInDB, Creator
from . import utils as ut
from ..database import get_session
from ..auth.queries import get_current_user

from . import queries as qr

router = APIRouter(prefix="/users")

@router.get("/", response_model=List[UserInDB])
async def get_users(
    skip: int = 0, 
    limit: int = 10, 
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    await ut.admin_check(user)
    users = await qr.get_users_list(session, skip, limit)
    return users

@router.get("/@{username}", response_model=Creator)
async def get_user_by_username(
    username:str, 
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):  
    if current_user:
        user = await qr.get_user_by_username(session, username)

        if user is None:
            raise HTTPException(status_code=400, detail="User not found")
        
        return await user.to_creator_pydantic()

@router.get("/{id}", response_model=BaseUser)
async def get_user_by_id(
    id:int, 
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):  
    await ut.admin_check(current_user)
    user = await qr.get_user_by_id(session, id)

    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    
    return await user.to_pydantic()