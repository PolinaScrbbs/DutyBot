from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..models.users import User, Duty, Group

async def get_attendants(students: List[User]) -> List[User]:
    student_duties = []

    for student in students:
        duties_count = await student.dities_count
        student_duties.append((student, duties_count))
    
    sorted_students = sorted(student_duties, key=lambda x: x[1])
    
    return [student for student, _ in sorted_students[:2]]

async def put_duty(session: AsyncSession, attendants: List[User]):
    for attendant in attendants:
        duty = Duty(
            attendant_id=attendant.id
        )

        session.add(duty)

    await session.commit()
    await session.close()

async def get_group_duties(session: AsyncSession, group_id: int) -> List[Duty]:
    try:
        result = await session.execute(
            select(Duty)
            .join(Duty.attendant)
            .where(User.group_id == group_id)
            .order_by(User.surname, desc(Duty.date))
            .options(selectinload(Duty.attendant))
        )

        duties = result.scalars().all()
        return duties
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    