from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists

from ..user.models import User, Role
from ..user.queries import get_user_by_id

from .models import Duty


async def post_duties(
    session: AsyncSession,
    current_user: User,
    attendant_ids: List[int]
) -> None:

    duties = []

    for id in attendant_ids:
        if current_user.role == Role.ELDER:
            print(id)
            student = await get_user_by_id(session, id)
            if current_user.group_id != student.group_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can't set shifts for students of another group",
                )

        duty = Duty(attendant_id = id)
        duties.append(duty)

    session.add_all(duties)
    await session.commit()