from typing import List, Optional
from database import get_async_session
from .models.users import Token
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from .models.users import User, Specialization, Group, Application
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
    finally:
        await session.close()

async def get_user(session: AsyncSession, username: str) -> User:
    try:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalars().one_or_none()
        return user
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
async def get_group(session: AsyncSession, id: int) -> Group:
    try:
        result = await session.execute(
            select(Group).where(Group.id == id)
        )
        group = result.scalars().one_or_none()

        return group if group else None
    
    except Exception as e:
        print(f"Error: {e}")
        return None

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
    
    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        await session.close()

async def get_groups(session: AsyncSession) -> List[Group]:
    try:
        result = await session.execute(
            select(Group)
        )

        groups = result.scalars().all()

        return groups
    
    except Exception as e:
        print(f"Error: {e}")
        return []

async def get_groups_without_application_from_user(session: AsyncSession, user_id) -> List[Group]:
    try:
        groups = await get_groups(session)

        groups_with_application = await session.execute(
            select(Application.group_id).where(Application.sending_id == user_id)
            )
        groups_with_application_ids = groups_with_application.scalars().all()

        groups_without_application = [group for group in groups if group.id not in groups_with_application_ids]

        return groups_without_application
    
    except Exception as e:
        print(f"Error: {e}")
        return []
    
    finally:
        await session.close()


async def send_application(session: AsyncSession, application_type: Enum, user_id: int, group_id: Optional[int]) -> Application:
    application = Application(
        type = application_type,
        sending_id = user_id,
        group_id = group_id
    )

    try:
        session.add(application)
        await session.commit()
        return application
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    finally:
        await session.close()

async def get_application(session: AsyncSession, application_type: Enum, user_id: int, group_id: Optional[int]) -> Application:
    try:
        result = await session.execute(
            select(Application).where(
                Application.type==application_type, 
                Application.sending_id==user_id, 
                Application.group_id==group_id
            )
        )

        application = result.scalars().one_or_none()

        return application
    
    except Exception as e:
        print(f"Error: {e}")
        return None