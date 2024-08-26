from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.users import User, Duty

async def assign_attendants(students: List[User], skipped_students: Optional[List[User]]) -> List[User]:
    if skipped_students:
        skipped_set = set(skipped_students)
        available_students = [student for student in students if student not in skipped_set]
    else:
        available_students = students

    student_duties = []

    for student in available_students:
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
    