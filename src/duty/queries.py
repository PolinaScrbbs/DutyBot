from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.models import User, Role
from ..user.queries import get_user_by_id

from .models import Duty
from .schemes import Student, DutyWithOutId


async def post_duties(
    session: AsyncSession, current_user: User, attendant_ids: List[int]
) -> None:

    duties = []

    for id in attendant_ids:
        if current_user.role == Role.ELDER:
            student = await get_user_by_id(session, id)
            if current_user.group_id != student.group_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can't set shifts for students of another group",
                )

        duty = Duty(attendant_id=id)
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
    session: AsyncSession, current_user: User, group_id: int
) -> List[Tuple[User, List[Duty]]]:
    await duty_protection(current_user, group_id)

    result = await session.execute(
        select(User).where(User.group_id == group_id).options(selectinload(User.duties))
    )

    users = result.scalars().all()
    return [(user, user.duties) for user in users]


async def get_group_duties(
    session: AsyncSession, current_user: User, group_id: int
) -> List[DutyWithOutId]:

    attendants_data = await get_users_data(session, current_user, group_id)
    duties_with_out_id = []

    for user, duties in attendants_data:
        duties_count = len(duties)
        last_duty = max((duty.date for duty in duties), default=None)

        attendant = Student(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            duties_count=duties_count,
            last_duty=last_duty,
        )

        for duty in duties:
            duties_with_out_id.append(
                DutyWithOutId(attendant=attendant, date=duty.date)
            )

    if duties_with_out_id == []:
        raise HTTPException(status.HTTP_204_NO_CONTENT)

    return duties_with_out_id


async def get_attendants(session: AsyncSession, students: List[User]) -> List[Student]:
    student_duties = []

    for student in students:
        duties_count = await student.duties_count(session)
        student_duties.append((student, duties_count))

    sorted_students = sorted(student_duties, key=lambda x: x[1])

    top_students = sorted_students[:2]

    return [
        Student(
            id=student.id,
            username=student.username,
            full_name=student.full_name,
            duties_count=duties_count,
            last_duty=student.last_duty,
        )
        for student, duties_count in top_students
    ]
