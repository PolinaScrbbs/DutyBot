from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.schemes import UserCreate, UserResponse
from ..database import get_session

from .schemes import TokenResponse, LoginForm
from . import queries as qr

router = APIRouter(prefix="/auth")

@router.post("/registration/", response_model=UserResponse)
async def create_user(user_create: UserCreate, session: AsyncSession = Depends(get_session)):
    user = await qr.registration_user(session, user_create)
    return UserResponse(
        message="User created successfully",
        user=await user.to_pydantic()
    )

@router.post("/login/", response_model=TokenResponse)
async def get_token(user_data: LoginForm, session: AsyncSession = Depends(get_session)):
    msg, token = await qr.login(session, user_data.login, user_data.password)
    return TokenResponse(
        message=msg,
        token=token.token
    )