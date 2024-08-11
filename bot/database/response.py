from typing import List
from database import get_async_session
from .models.users import Token
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from .models.users import User, Specialization, Group, GroupRequest
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
        return user
    
    except Exception as e:
        return str(e)
    
async def get_group(session: AsyncSession, id: int) -> Group:
    try:
        result = await session.execute(
            select(Group).where(Group.id == id)
        )
        group = result.scalars().one_or_none()

        return group if group else None
    
    except Exception as e:
        return str(e)

async def create_group(session: AsyncSession, title: str, specialization: Specialization, course_number: int, creator_username: str) -> Group:
    user = await get_user(session, creator_username)

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
        await session.close()

async def get_groups(session: AsyncSession) -> List[Group]:
    try:
        result = await session.execute(
            select(Group)
        )

        groups = result.scalars().all()

        return groups
    
    finally:
        pass
        # await session.close()

async def send_group_request(session: AsyncSession, request_type: Enum, requesting_username: str, group_id: int) -> GroupRequest:
    user = await get_user(session, requesting_username)
    group = await get_group(session, group_id)

    request = GroupRequest(
        type = request_type,
        requesting_id = user.id,
        group_id = group.id
    )

    try:
        session.add(request)
        await session.commit()
        return request, group
    except:
        return None, None
    finally:
        await session.close()