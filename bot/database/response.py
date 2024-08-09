from database import get_async_session
from .models.users import Token
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from .models.users import User, Specialization, Group
from enum import Enum

# async def save_token(user_id, token):
#     async with get_async_session() as session:
#         new_token = Token(tg_id=user_id, token=token)
#         session.add(new_token)
#         await session.commit()

# async def get_token(tg_id):
#     async with get_async_session() as session:
#         stmt = select(Token).where(Token.tg_id == tg_id)
#         result = await session.execute(stmt)
#         user_token = result.scalar_one_or_none()
#         return user_token.token if user_token else None

async def get_specialization(text: str) -> Specialization:
    for spec in Specialization:
        if spec.value == text:
            return spec
    raise ValueError(f"Specialization с текстом '{text}' не найдена.")

async def register_user(session: AsyncSession, username: str, password: str, name: str, surname: str, patronymic: str) -> User:
    user = User(
        username=username,
        name=name,
        surname=surname,
        patronymic=patronymic,
    )
    
    user.set_password(password)
    
    try:
        session.add(user)
        await session.commit()
        return user
    except IntegrityError:
        await session.rollback()
        raise Exception("Пользователь с таким именем пользователя или электронной почтой уже существует")
    except Exception as e:
        await session.rollback()
        raise Exception(f"Произошла ошибка при регистрации пользователя: {e}")

async def get_user(session: AsyncSession, username: str) -> User:
    try:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalars().one_or_none()
        print(User)
        return user
    
    except Exception as e:
        return str(e)

async def create_group(session: AsyncSession, title: str, specialization: Specialization, course_number: int, creator_username: str) -> Group:
    user = await get_user(session, creator_username)
    print(course_number, type(course_number))
    group = Group(
        title = title,
        specialization = specialization,
        course_number = course_number,
        creator_id = user.id
    )

    try:
        session.add(group)
        await session.commit()
        return group
    finally:
        session.close
