import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from enum import Enum as BaseEnum
from ...config import SECRET_KEY

class Base(DeclarativeBase):
    pass

class Role(BaseEnum):
    ADMIN = "Администратор"
    ELDER = "Староста"
    STUDENT = "Студент"

class User(Base):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    role = mapped_column(Enum(Role), default=Role.STUDENT, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    surname: Mapped[str] = mapped_column(String(64), nullable=False)
    patronymic: Mapped[str] = mapped_column(String(64), nullable=False)
    # email: Mapped[str] = mapped_column(String(40), default=None, unique=True, nullable=True)
    # phone_number: Mapped[str] = mapped_column(CHAR(15), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(True), server_default=func.now())
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    mailing_consent: Mapped[bool] = mapped_column(default=False, nullable=False)

    token: Mapped["Token"] = relationship("Token", back_populates="user")

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

    id = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    user_id = mapped_column(Integer, ForeignKey("users.id"))

    user: Mapped["User"] = relationship("User", back_populates="token")