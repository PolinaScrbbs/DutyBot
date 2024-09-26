from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.models import User, Role
from ..user.queries import get_user_by_id

from .models import Duty
from .schemes import BaseStudent, Student, DutyWithOutId


async def post_duties(
    session: AsyncSession, current_user: User, attendant_ids: List[int]
) -> None:

    duties = []

    for student_id in attendant_ids:
        student = await get_user_by_id(session, student_id)
        if current_user.group_id != student.group_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't set shifts for students of another group",
            )

        duty = Duty(attendant_id=student_id)
        duties.append(duty)

    session.add_all(duties)
    await session.commit()


async def duty_protection(
    current_user: User,
    group_id: int,
) -> Optional[HTTPException]:

    if current_user.role != Role.ADMIN:
        if current_user.group_id != group_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to the duties of someone else's group",
            )


async def get_users_data(
    session: AsyncSession,
    current_user: User,
    group_id: Optional[int],
    attendant_id: Optional[int] = None,
) -> List[Tuple[User, List[Duty]]]:
    await duty_protection(current_user, group_id)

    query = select(User).where(User.group_id == group_id, User.id != current_user.id)

    if attendant_id is not None:
        query = query.where(User.id == attendant_id)

    query = query.options(selectinload(User.duties))

    result = await session.execute(query)

    users = result.scalars().all()
    return [(user, user.duties) for user in users]


async def get_group_duties(
    session: AsyncSession,
    current_user: User,
    group_id: Optional[int] = None,
    attendant_id: Optional[int] = None,
) -> List[DutyWithOutId]:

    attendants_data = await get_users_data(
        session, current_user, group_id, attendant_id
    )
    duties_with_out_id = []

    for user, duties in attendants_data:
        duties_count = len(duties)
        last_duty = max((duty.date for duty in duties), default=None)

        attendant = Student(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            duties_count=duties_count,
            last_duty=last_duty.strftime("%H:%M %d-%m-%Y") if last_duty else last_duty,
        )

        for duty in duties:
            formatted_date = await duty.formatted_date
            duties_with_out_id.append(
                DutyWithOutId(attendant=attendant, date=formatted_date)
            )

    if duties_with_out_id == []:
        raise HTTPException(status.HTTP_204_NO_CONTENT)

    return duties_with_out_id


async def get_group_attendants(
    session: AsyncSession, group_id: int, missed_students_id: List[int]
) -> List[BaseStudent]:

    result = await session.execute(
        select(
            User.id,
            User.username,
            User.full_name,
            func.count(Duty.id).label("duties_count"),
        )
        .join(Duty, Duty.attendant_id == User.id)
        .where(User.group_id == group_id, User.id.notin_(missed_students_id))
        .group_by(User.id)
        .order_by(func.count(Duty.id).desc())
    )

    students = result.all()
    top_students = students[:2]

    return [
        BaseStudent(
            id=student.id,
            username=student.username,
            full_name=student.full_name,
        )
        for student in top_students
    ]
