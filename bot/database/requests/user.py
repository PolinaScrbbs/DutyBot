from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.users import User, Token


async def reg_user(
    session: AsyncSession, username: str, password: str, full_name: str
) -> User:
    parts = full_name.split()
    surname, name, patronymic = parts

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
        raise Exception(
            "Пользователь с таким именем пользователя или электронной почтой уже существует"
        )
    except Exception as e:
        await session.rollback()
        raise Exception(f"Произошла ошибка при регистрации пользователя: {e}")
    finally:
        await session.close()


async def auth_user(session: AsyncSession, login: str, password: str):
    try:
        result = await session.execute(select(User).where(User.username == login))

        user = result.scalars().one_or_none()

        if user != None and user.check_password(password):
            token = user.generate_token()
            token = Token(user_id=user.id, token=token)
            session.add(token)
            await session.commit()

        else:
            raise Exception(f"*Неверный пароль*")

        return user

    # except Exception as e:
    #     await session.rollback()
    #     raise Exception(f"❌ Ошибка авторизации {e}")
    finally:
        await session.close()


async def get_user_by_username(session: AsyncSession, username: str) -> User:
    try:
        result = await session.execute(select(User).where(User.username == username))

        user = result.scalars().one_or_none()
        return user

    except Exception as e:
        print(f"Error: {e}")
        return None


async def get_user_by_id(session: AsyncSession, id: int) -> User:
    try:
        result = await session.execute(select(User).where(User.id == id))

        user = result.scalars().one_or_none()
        return user

    except Exception as e:
        print(f"Error: {e}")
        return None


# async def get_user_by_id_with_duties(session: AsyncSession, id: int) -> User:
#     try:
#         result = await session.execute(
#             select(User).where(User.id == id).options(
#                 selectinload(User.duties)
#             )
#         )

#         user = result.scalar_one_or_none()
#         return user

#     except Exception as e:
#         print(f"Error: {e}")
#         return None
