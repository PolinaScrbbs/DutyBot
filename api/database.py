from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import config as conf


engine = create_async_engine(
    conf.database_url,
    echo=True,
    pool_pre_ping=True,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "server_settings": {
            "jit": "off"
        }
    }
)


async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    future=True
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

class Base(DeclarativeBase):
    pass