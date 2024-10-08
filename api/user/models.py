from typing import Optional
import bcrypt
from fastapi import HTTPException, status
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
from sqlalchemy import select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from enum import Enum as BaseEnum
from config import SECRET_KEY

from ..duty.models import Duty
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
    avatar_url = Column(String, default = None, unique=True, nullable=True)

    token = relationship("Token", back_populates="user", cascade="all, delete-orphan")
    created_group = relationship(
        "Group", back_populates="creator", foreign_keys="[Group.creator_id]"
    )
    group = relationship(
        "Group", back_populates="students", foreign_keys="[User.group_id]"
    )
    sent_application = relationship(
        "Application", back_populates="sending", cascade="all, delete-orphan"
    )
    duties = relationship(
        "Duty", back_populates="attendant", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    async def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), self.hashed_password.encode("utf-8")
        )

    async def generate_token(self, expires_in: int = 4800) -> str:
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

    async def to_pydantic(self) -> BaseUser:
        return BaseUser(
            id=self.id,
            role=self.role,
            username=self.username,
            full_name=self.full_name,
            group_id=self.group_id,
            avatar_url=self.avatar_url,
            created_at=self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    async def duties_count(self, session: AsyncSession) -> int:
        result = await session.execute(
            select(func.count(Duty.id)).where(Duty.attendant_id == self.id)
        )
        return result.scalar_one()

    # async def last_duty(self, session: AsyncSession) -> datetime:
    #     result = await session.execute(
    #         select(Duty.date)
    #         .where(Duty.attendant_id == self.id)
    #         .order_by(Duty.date.desc())
    #         .limit(1)
    #     )

    #     return result.scalar_one_or_none()


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String(256), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="token")

    async def verify_token(self, session: AsyncSession, user: Optional[User]):
        try:
            jwt.decode(self.token, SECRET_KEY, algorithms=["HS256"])
            return status.HTTP_200_OK, "The user's token has been verified", self

        except jwt.ExpiredSignatureError:
            return await self.refresh_token(session, user)

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def refresh_token(self, session: AsyncSession, user: Optional[User]):
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        new_token = await user.generate_token()

        self.token = new_token
        session.add(self)
        await session.commit()

        return status.HTTP_200_OK, "The user's token has been updated", self
