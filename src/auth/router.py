from fastapi import Depends, APIRouter, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.schemes import UserCreate, UserResponse
from ..database import get_session

from .schemes import LoginForm, TokenResponse
from . import queries as qr
from .validators import RegistrationValidator

router = APIRouter(prefix="/auth")


@router.post("/registration", response_class=Response)
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
    return Response(
        content=UserResponse(
            message="User created successfully", 
            user=await user.to_pydantic()
        ).dict(),
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/login", response_class=JSONResponse)
async def get_token(
    login_form: LoginForm,
    session: AsyncSession = Depends(get_session),
):
    code, message, token = await qr.login(
        session, login_form.login, login_form.password
    )
    return JSONResponse(
        content=TokenResponse(message=message, token=token).dict(), status_code=code
    )
