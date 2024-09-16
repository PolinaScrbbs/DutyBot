from typing import List
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .models import User
from .schemes import UserCreate, UserInDB, UserResponse
from ..database import get_session

from . import queries as qr

router = APIRouter()

@router.get("/users/", response_model=List[UserInDB])
async def read_users(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    users = await qr.get_users_list(session, skip, limit)
    return users

@router.post("/users/", response_model=UserResponse)
async def create_user(user_create: UserCreate, session: AsyncSession = Depends(get_session)):
    user = await qr.registration_user(session, user_create)
    return UserResponse(
        message="User created successfully",
        user=await user.to_pydantic()
    )