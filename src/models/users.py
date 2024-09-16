import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    Enum,
    Table,
    CheckConstraint,
    select,
)
from sqlalchemy.orm import relationship, DeclarativeBase, validates, backref
from enum import Enum as BaseEnum
from sqlalchemy.ext.asyncio import AsyncSession
from config import SECRET_KEY


class Base(DeclarativeBase):
    pass


class Specialization(BaseEnum):
    ECONOMIST = "Экономист"
    INFORMATION_SYSTEMS_SPECIALIST = "Специалист по ИС"
    WEB_DEVELOPER = "WEB-разработчик"
    LANDSCAPE_DESIGNER = "Ландшафтный дизайнер"
    LIGHT_INDUSTRY_WORKER = "Рабочий легкой промышленности"
    HAIRDRESSER = "Парикмахер"
    COSMETOLOGIST = "Косметолог"
    DESIGNER = "Дизайнер"
    FIRE_FIGHTER = "Пожарный"
    BUILDER = "Строитель"
    BIM_SPECIALIST = "BIM-специалист"
    BANKER = "Банкир"
    FINANCIER = "Финансист"
    WELDER = "Сварщик"
    BAKER_PASTRY_CHEF = "Пекарь-кондитер"
    INDUSTRIAL_FURNITURE_DESIGNER = "Промышленный дизайнер мебели"
    INTERIOR_DESIGNER = "Дизайнер интерьера"
    GENERAL_CONSTRUCTION_WORKER = "Общестроительный рабочий"
    ATOMIC_ENGINEER = "Атомщик"


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    title = Column(String(32), unique=True, nullable=False)
    specialization = Column(Enum(Specialization), nullable=False)
    course_number = Column(Integer, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "course_number >= 1 AND course_number <= 4", name="course_number_range"
        ),
    )

    @validates("course_number")
    def validate_course_number(self, key, value):
        if not (1 <= value <= 4):
            raise ValueError("Номер курса должен быть от 1 до 4")
        return value

    creator = relationship(
        "User", back_populates="created_group", foreign_keys=[creator_id]
    )
    students = relationship(
        "User",
        back_populates="group",
        foreign_keys="[User.group_id]",
        cascade="all, delete-orphan",
    )
    applications = relationship(
        "Application", back_populates="group_applications", cascade="all, delete-orphan"
    )


class Role(BaseEnum):
    ADMIN = "Администратор"
    ELDER = "Староста"
    STUDENT = "Студент"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True, nullable=False)
    hashed_password = Column(String(1024), nullable=False)
    role = Column(Enum(Role), default=Role.STUDENT, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), default=None, nullable=True)
    name = Column(String(64), nullable=False)
    surname = Column(String(64), nullable=False)
    patronymic = Column(String(64), nullable=False)
    created_at = Column(DateTime(True), server_default=func.now())

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

    @property
    async def full_name(self) -> str:
        return f"{self.surname} {self.name} {self.patronymic}"

    async def duties_count(self, session: AsyncSession) -> int:
        result = await session.execute(
            select(func.count(Duty.id)).where(Duty.attendant_id == self.id)
        )
        return result.scalar_one()


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String(256), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="token")


class ApplicationType(BaseEnum):
    GROUP_JOIN = "На вступление в группу"
    BECOME_ELDER = "Стать старостой"


class ApplicationStatus(BaseEnum):
    SENT = "Отправлен"
    ADOPTED = "Принят"
    REJECTED = "Отклонен"


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    type = Column(Enum(ApplicationType), nullable=False)
    status = Column(
        Enum(ApplicationStatus), default=ApplicationStatus.SENT, nullable=False
    )
    sending_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True, default=None)
    last_update_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    sending = relationship("User", back_populates="sent_application")
    group_applications = relationship("Group", back_populates="applications")


class Duty(Base):
    __tablename__ = "duties"

    id = Column(Integer, primary_key=True)
    attendant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(True), server_default=func.now())

    attendant = relationship("User", back_populates="duties")

    @property
    async def formatted_date(self) -> str:
        return self.date.strftime("%H:%M %d-%m-%Y")
