from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists

from ..user.models import User, Role
from ..user.queries import get_user_by_id

from .models import Duty
from .schemes import Attendant, AttendantWithDuties


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


async def get_group_attendants(
    session: AsyncSession, current_user: User, group_id: int
) -> List[AttendantWithDuties]:
    if current_user.role != Role.ADMIN and current_user.group_id != group_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to the duties of someone else's group",
        )

    result = await session.execute(
        select(User).where(User.group_id == group_id).options(selectinload(User.duties))
    )

    users = result.scalars().all()

    attendants_with_duties = []

    for user in users:
        duties = user.duties
        duties_count = len(duties)
        last_duty = max((duty.date for duty in duties), default=None)

        attendant = Attendant(
            username=user.username,
            full_name=user.full_name,
            duties_count=duties_count,
            last_duty=last_duty,
        )

        attendant_duties = []
        for duty in duties:
            pydantic_duty = await duty.duty_to_pydantic(session)
            attendant_duties.append(pydantic_duty)

        attendants_with_duties.append(
            AttendantWithDuties(attendant=attendant, duties=attendant_duties)
        )

    return attendants_with_duties
