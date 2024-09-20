from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import relationship, DeclarativeBase

from .schemes import Attendant, DutyWithOutId


class Base(DeclarativeBase):
    pass


class Duty(Base):
    __tablename__ = "duties"

    id = Column(Integer, primary_key=True)
    attendant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(True), server_default=func.now())

    attendant = relationship("User", back_populates="duties")

    @property
    async def formatted_date(self) -> str:
        return self.date.strftime("%H:%M %d-%m-%Y")

    # async def attendant_to_pydantic(self, session: AsyncSession) -> Attendant:
    #     return Attendant(
    #         username = self.attendant.username,
    #         full_name = self.attendant.full_name,
    #         duties_count = await self.attendant.duties_count(session),
    #         last_duty = await self.attendant.last_duty(session)
    #     )

    # async def duty_to_pydantic(self, session: AsyncSession) -> DutyWithOutId:
    #     return DutyWithOutId(
    #         attendant = await self.attendant_to_pydantic(session),
    #         date = self.date
    #     )
