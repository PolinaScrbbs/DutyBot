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
from .schemes import BaseGroup

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
    # applications = relationship(
    #     "Application", back_populates="group_applications", cascade="all, delete-orphan"
    # )

    async def to_pydantic(self):
        return BaseGroup(
           title = self.title,
           specialization = self.specialization,
           course_number = self.course_number,
           creator_id =  self.creator_id
        )