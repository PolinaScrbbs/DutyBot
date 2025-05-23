from datetime import datetime
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import func, desc
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.models import User, Role
from ..user.queries import get_user_by_id

from .models import Duty
from .schemes import BaseStudent, Student, DutyWithOutId


# Создание новых дежурств
async def post_duties(
    session: AsyncSession, current_user: User, attendant_ids: List[int]
) -> None:

    duties = []

    for student_id in attendant_ids:
        student = await get_user_by_id(session, student_id)
        if current_user.group_id != student.group_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете назначать дежурства студентам из другой группы",
            )

        duty = Duty(attendant_id=student_id)
        duties.append(duty)

    session.add_all(duties)
    await session.commit()


# Проверка доступа к дежурствам группы
async def duty_protection(
    current_user: User,
    group_id: int,
) -> Optional[HTTPException]:

    if current_user.role != Role.ADMIN:
        if current_user.group_id != group_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет доступа к дежурствам чужой группы",
            )


# Получение данных о пользователях и их дежурствах
async def get_users_data(
    session: AsyncSession,
    current_user: User,
    group_id: Optional[int],
    attendant_id: Optional[int] = None,
    limit: int = 10,
    offset: int = 0,
) -> List[Tuple[User, Duty]]:
    await duty_protection(current_user, group_id)

    duty_query = (
        select(Duty)
        .join(Duty.attendant)
        .options(selectinload(Duty.attendant).selectinload(User.duties))
    )

    if current_user.role != Role.STUDENT:
        duty_query = duty_query.where(
            User.group_id == group_id, User.id != current_user.id
        )
    else:
        duty_query = duty_query.where(
            User.group_id == group_id, User.id == current_user.id
        )

    if attendant_id is not None:
        duty_query = duty_query.where(User.id == attendant_id)

    duty_query = duty_query.order_by(Duty.date.desc()).offset(offset).limit(limit)

    result = await session.execute(duty_query)
    duties = result.scalars().all()

    return [(duty.attendant, duty) for duty in duties]


# Получение списка дежурств по группе
async def get_group_duties(
    session: AsyncSession,
    current_user: User,
    group_id: Optional[int] = None,
    attendant_id: Optional[int] = None,
    limit: int = 10,
    offset: int = 0,
) -> List[DutyWithOutId]:

    if group_id is None:
        group_id = current_user.group_id

    duties_data = await get_users_data(
        session, current_user, group_id, attendant_id, limit, offset
    )

    if not duties_data:
        raise HTTPException(status.HTTP_204_NO_CONTENT)

    duties_with_out_id = []

    for user, duty in duties_data:
        attendant = Student(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            duties_count=len(user.duties),
            last_duty=(
                max((d.date for d in user.duties), default=None).strftime(
                    "%H:%M %d-%m-%Y"
                )
                if user.duties
                else None
            ),
        )

        formatted_date = await duty.formatted_date
        duties_with_out_id.append(
            DutyWithOutId(attendant=attendant, date=formatted_date)
        )

    return duties_with_out_id


# Получение списка студентов, которым можно назначить дежурство
async def get_group_attendants(
    session: AsyncSession, elder_id: int, group_id: int, missed_students_id: List[int]
) -> List[BaseStudent]:
    result = await session.execute(
        select(
            User.id,
            User.username,
            User.full_name,
            func.count(Duty.id).label("duties_count"),
            func.max(Duty.date).label("last_duty_date"),
        )
        .outerjoin(Duty, Duty.attendant_id == User.id)
        .where(
            User.group_id == group_id,
            User.id != elder_id,
            User.id.notin_(missed_students_id),
        )
        .group_by(User.id, User.username, User.full_name)
        .order_by(User.full_name)
    )

    students = result.all()

    sorted_students = sorted(students, key=lambda x: (x[3], x[4] or datetime.min))
    bottom_students = sorted_students[:2]

    return [
        BaseStudent(
            id=student.id,
            username=student.username,
            full_name=student.full_name,
        )
        for student in bottom_students
    ]


# Получение текущих дежурных студентов
async def get_current_attendants(session: AsyncSession, group_id: int):
    result = await session.execute(
        select(User.id, User.username, User.full_name)
        .join(Duty, Duty.attendant_id == User.id)
        .where(User.group_id == group_id)
        .order_by(desc(Duty.date))
        .limit(2)
    )
    current_attendants = result.all()

    return [
        BaseStudent(
            id=student.id,
            username=student.username,
            full_name=student.full_name,
        )
        for student in current_attendants
    ]
