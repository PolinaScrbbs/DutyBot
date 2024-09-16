import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    Enum,
)
from sqlalchemy.orm import relationship, DeclarativeBase, validates, backref
from enum import Enum as BaseEnum
from config import SECRET_KEY

from ..group.models import Base
from .schemes import BaseUser

class Role(BaseEnum):
    ADMIN = "Администратор"
    ELDER = "Староста"
    STUDENT = "Студент"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    role = Column(Enum(Role), default=Role.STUDENT, nullable=False)
    username = Column(String(32), unique=True, nullable=False)
    hashed_password = Column(String(1024), nullable=False)
    full_name = Column(String(100), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), default=None, nullable=True)
    created_at = Column(DateTime(True), server_default=func.now())

    token = relationship("Token", back_populates="user", cascade="all, delete-orphan")
    created_group = relationship(
        "Group", back_populates="creator", foreign_keys="[Group.creator_id]"
    )
    group = relationship(
        "Group", back_populates="students", foreign_keys="[User.group_id]"
    )
    # sent_application = relationship(
    #     "Application", back_populates="sending", cascade="all, delete-orphan"
    # )
    # duties = relationship(
    #     "Duty", back_populates="attendant", cascade="all, delete-orphan"
    # )

    def set_password(self, password: str) -> None:
        self.hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), self.hashed_password.encode("utf-8")
        )

    def generate_token(self, expires_in: int = 3600) -> str:
        payload = {
            "user_id": self.id,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def get_token(self) -> "Token":
        return self.tokens[0] if self.tokens else None

    def delete_token(self, token_id: int) -> None:
        token_to_delete = next(
            (token for token in self.tokens if token.id == token_id), None
        )
        if token_to_delete:
            self.tokens.remove(token_to_delete)

    def verify_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload["user_id"]
        except jwt.ExpiredSignatureError:
            raise Exception("Токен истек")
        except jwt.InvalidTokenError:
            raise Exception("Неверный токен")
        
    async def to_pydantic(self) -> BaseUser:
        return BaseUser(
            id=self.id,
            role=self.role,
            username=self.username,
            full_name=self.full_name,
            created_at=self.created_at
        )

    # async def duties_count(self, session: AsyncSession) -> int:
    #     result = await session.execute(
    #         select(func.count(Duty.id)).where(Duty.attendant_id == self.id)
    #     )
    #     return result.scalar_one()

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String(256), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="token")