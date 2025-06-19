from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import config as conf
# Создаем синхронный engine с увеличенными таймаутами
engine = create_engine(
    conf.database_url,
    echo=True,
    # pool_pre_ping=True,
    # pool_size=20,
    # max_overflow=10,
    # pool_timeout=30,  # 30 секунд ожидания соединения из пула
    # pool_recycle=3600
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

def get_session():
    """Генератор сессий (синхронный)"""
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

class Base(DeclarativeBase):
    pass
