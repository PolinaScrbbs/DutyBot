from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import relationship, DeclarativeBase


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