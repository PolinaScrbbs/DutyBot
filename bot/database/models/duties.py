# from sqlalchemy import Column, DateTime, Integer, ForeignKey, func
# from sqlalchemy.orm import relationship

# from .groups import Base

# class Duty(Base):
#     __tablename__ = 'duties'

#     id = Column(Integer, primary_key=True)
#     attendant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     date = Column(DateTime(True), server_default=func.now())

#     attendant = relationship("User", back_populates="duties")
