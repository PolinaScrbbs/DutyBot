from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from .schemes import UserInDB
from ..database import get_session

from . import queries as qr

router = APIRouter()

@router.get("/users/", response_model=List[UserInDB])
async def read_users(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    users = await qr.get_users_list(session, skip, limit)
    return users