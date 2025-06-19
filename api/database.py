from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import config as conf

# Убедитесь, что в config.py строка подключения формируется правильно:
# self.database_url = f"postgresql+asyncpg://{self.db_user}:{quote_plus(self.db_user_password)}@{self.host}:{self.port}/{self.db_name}?sslmode=require"

engine = create_async_engine(
    conf.database_url,
    echo=True,  # Логирование запросов (можно отключить в продакшене)
    pool_pre_ping=True,  # Проверка соединений перед использованием
    pool_size=20,  # Размер пула соединений
    max_overflow=10,  # Максимальное количество переполнений пула
    pool_timeout=30,  # Таймаут ожидания соединения
    pool_recycle=3600,  # Пересоздавать соединения каждый час
    connect_args={
        "statement_cache_size": 0,  # Полностью отключаем кэш
        "prepared_statement_cache_size": 0,  # Отключаем prepared statements
        "server_settings": {
            "jit": "off",
            "application_name": "your_app_name",
            "timezone": "UTC"
        },
        "ssl": "require",  # Явное указание SSL
        "timeout": 10,  # Таймаут подключения
        "command_timeout": 30  # Таймаут выполнения команд
    }
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Не сбрасывать объекты после коммита
    autoflush=False,  # Отключаем авто-сброс
    future=True  # Используем новый стиль API
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

class Base(DeclarativeBase):
    pass