# from sqlalchemy import Column, DateTime, Integer, String, Enum, ForeignKey, CheckConstraint, func
# from sqlalchemy.orm import relationship, validates
# from enum import Enum as BaseEnum
# from .users import Base, band_members, User

# class Department(BaseEnum):
#     ECONOMIST = "Экономист"
#     INFORMATION_SYSTEMS_SPECIALIST = "Специалист по ИС"
#     WEB_DEVELOPER = "WEB-разработчик"
#     LANDSCAPE_DESIGNER = "Ландшафтный дизайнер"
#     LIGHT_INDUSTRY_WORKER = "Рабочий легкой промышленности"
#     HAIRDRESSER = "Парикмахер"
#     COSMETOLOGIST = "Косметолог"
#     DESIGNER = "Дизайнер"
#     FIRE_FIGHTER = "Пожарный"
#     BUILDER = "Строитель"
#     BIM_SPECIALIST = "BIM-специалист"
#     BANKER = "Банкир"
#     FINANCIER = "Финансист"
#     WELDER = "Сварщик"
#     BAKER_PASTRY_CHEF = "Пекарь-кондитер"
#     INDUSTRIAL_FURMITURE_DESIGNER = "Промышленный дизайнер мебели"
#     INTERIOR_DESIGNER = "Дизайнер интерьера"
#     GENERAL_CONSTRUCTION_WORKER = "Общестроительный рабочий "
#     ATOMIC_ENGINEER = "Атомщик"

# class Group(Base):
#     __tablename__ = 'groups'
#     id = Column(Integer, primary_key=True)
#     title = Column(String(32), unique=True, nullable=False)
#     department = Column(Enum(Department), nullable=False)
#     cource_number = Column(Integer, nullable=False)
#     creator_id = Column(Integer, ForeignKey('User.id'), unique=True, nullable=False)
#     created_at = Column(DateTime(True), server_default=func.now())

#     __table_args__ = (
#         CheckConstraint('cource_number >= 1 AND cource_number <= 4', name='cource_number_range'),
#     )

#     @validates('cource_number')
#     def validate_cource_number(self, key, value):
#         if not (1 <= value <= 4):
#             raise ValueError("Номер курса должен быть от 1 до 4")
#         return value

#     creator = relationship("User", back_populates="created_groups")
#     users = relationship("User", secondary=band_members, back_populates="groups")