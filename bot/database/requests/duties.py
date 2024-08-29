from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..models.users import User, Duty, Group

async def get_attendants(session: AsyncSession, students: List[User]) -> List[User]:
    student_duties = []

    for student in students:
        duties_count = await student.duties_count(session)
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
    
    finally:
        await session.close()
    
async def get_group_duties_count(session: AsyncSession, group_id: int) -> List[dict]:
    try:
        result = await session.execute(
            select(
                User.username,
                User.surname,
                User.name,
                User.patronymic,
                func.count(Duty.id).label('duties_count'),
                func.max(Duty.date).label('last_duty_date')
            )
            .join(Duty.attendant)
            .where(User.group_id == group_id)
            .group_by(User.id)
            .order_by(func.count(Duty.id).desc(), User.surname)
        )

        duties_count = [
            {
                "username": row['username'],
                "full_name": f"{row['surname']} {row['name']} {row['patronymic']}",
                "duties_count": row['duties_count'],
                "last_duty_date": row['last_duty_date']
            }
            for row in result.mappings().all()
        ]

        return duties_count

    except Exception as e:
        print(f"Error: {e}")
        return []
    
    finally:
        await session.close()

async def get_user_duties(session: AsyncSession, user_id: int) ->  Tuple[Optional[Tuple[List[Duty]]], Optional[Duty]]:
    try:
        result = await session.execute(
            select(Duty).where(Duty.attendant_id == user_id)
            .order_by(desc(Duty.date))
            .options(selectinload(Duty.attendant))
        )

        duties = result.scalars().all()

        if not duties:
            return None, None
        
        last_duty = duties[0]
        return duties, last_duty
    
    except Exception as e:
        print(f"Error: {e}")
        return []
    
    finally:
        await session.close()