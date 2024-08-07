from database import get_async_session
from .models.users import Token
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from .models.users import User

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