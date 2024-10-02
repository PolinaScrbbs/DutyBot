from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    func,
    Enum,
)
from sqlalchemy.orm import relationship
from enum import Enum as BaseEnum

from ..duty.models import Base


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
