from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..user.queries import get_user_by_username, get_user_by_id
from ..user.models import User, Token
from ..user.schemes import UserCreate

async def registration_user(
    session: AsyncSession, user_create: UserCreate
) -> User:
    
    user = User(
        username=user_create.username,
        full_name=user_create.full_name
    )
    user.set_password(user_create.password)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user

async def get_user_token(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(Token).where(Token.user_id==user_id)
    )

    return result.scalar_one_or_none()

async def login(
    session: AsyncSession, login: str, password: str
) -> Token:
    
    user = await get_user_by_username(session, login)

    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    
    correct_password = await user.check_password(password)

    if not correct_password:
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    token = await get_user_token(session, user.id)

    if token is None:
        token = await user.generate_token()
        token = Token(user_id=user.id, token=token)
        msg = "A user token has been created"

        session.add(token)
        await session.commit()

    else:
        msg, token = await token.verify_token(session, user)

        if msg is None:
            msg = "The user's token has been verified"
    
    return msg, token

async def get_token(session:AsyncSession, token: str) -> Token:
    result = await session.execute(
        select(Token).where(Token.token==token)
    )

    return result.scalar_one_or_none()

async def verify_token_and_get_user(session: AsyncSession, token: str) -> User:
    token = await get_token(session, token)

    if token is None:
        raise HTTPException(status_code=400, detail="Token not found")
    
    await token.verify_token(session, None)
    user = await get_user_by_id(session, token.user_id)

    return user

async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str =  Depends(OAuth2PasswordBearer(tokenUrl="token"))
) -> User:
    user = await verify_token_and_get_user(session, token)
    return user