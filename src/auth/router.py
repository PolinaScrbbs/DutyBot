from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.schemes import UserCreate, UserResponse
from ..database import get_session

from .schemes import TokenResponse
from . import queries as qr
from .validators import RegistrationValidator

router = APIRouter(prefix="/auth")


@router.post("/registration", response_model=UserResponse)
async def create_user(
    user_create: UserCreate, session: AsyncSession = Depends(get_session)
):
    validator = RegistrationValidator(
        user_create.username,
        user_create.password,
        user_create.confirm_password,
        user_create.full_name,
        session,
    )
    await validator.validate()

    user = await qr.registration_user(session, user_create)
    return UserResponse(
        message="User created successfully", user=await user.to_pydantic()
    )


@router.post("/login", response_model=TokenResponse)
async def get_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    msg, token = await qr.login(session, form_data.username, form_data.password)
    return TokenResponse(message=msg, token=token.token)
