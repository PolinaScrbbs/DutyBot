import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func, Enum, Table
from sqlalchemy.orm import relationship, DeclarativeBase
from enum import Enum as BaseEnum
from ...config import SECRET_KEY

class Base(DeclarativeBase):
    pass

class Role(BaseEnum):
    ADMIN = "Администратор"
    ELDER = "Староста"
    STUDENT = "Студент"

band_members = Table(
    'band_members',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('group.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True, nullable=False)
    hashed_password = Column(String(1024), nullable=False)
    role = Column(Enum(Role), default=Role.STUDENT, nullable=False)
    name = Column(String(64), nullable=False)
    surname = Column(String(64), nullable=False)
    patronymic = Column(String(64), nullable=False)
    created_at = Column(DateTime(True), server_default=func.now())
    is_verified = Column(Boolean, default=False, nullable=False)
    mailing_consent = Column(Boolean, default=False, nullable=False)

    token = relationship("Token", back_populates="user")
    created_groups = relationship("Group", back_populates="creator", foreign_keys=["groups.creator_id"])
    groups = relationship("Group", secondary=band_members, back_populates="users")
    duties = relationship("Duty", back_populates="attendant")

    def set_password(self, password: str) -> None:
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))
    
    def generate_token(self, expires_in: int = 3600) -> str:
        payload = {
            "user_id": self.id,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def get_token(self) -> "Token":
        return self.tokens

    def delete_token(self, token_id: int) -> None:
        token_to_delete = next((token for token in self.tokens if token.id == token_id), None)
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
        
    # def get_inventory_items(self):
    #     inventory = self.inventory

    #     if inventory:
    #         items = inventory.items

    #         item_counts = {}
    #         for item in items:
    #             if item.title in item_counts:
    #                 item_counts[item.title] += 1
    #             else:
    #                 item_counts[item.title] = 1

    #         return item_counts
    #     else:
    #         return {}
        
class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String(256), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="token")