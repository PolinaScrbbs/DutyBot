from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.models import User
from ..user.queries import get_user_by_id
from ..duty.queries import duty_protection, get_students_data

from .models import Group, Specialization
from .schemes import BaseGroup, GroupInDB, Student, StudentWithDuties


async def get_groups_list(
    session: AsyncSession, skip: Optional[int], limit: Optional[int]
) -> List[GroupInDB]:

    result = await session.execute(
        select(Group)
        .options(
            selectinload(Group.creator).load_only(
                User.role, User.username, User.full_name
            ),
            selectinload(Group.students),
        )
        .offset(skip)
        .limit(limit)
    )

    return result.scalars().all()


async def create_group(
    session: AsyncSession, group_create: BaseGroup, creator_id: int
) -> BaseGroup:

    group = Group(
        title=group_create.title,
        specialization=Specialization(group_create.specialization),
        course_number=group_create.course_number,
        creator_id=creator_id,
    )

    user = await get_user_by_id(session, creator_id)

    session.add(group)
    user.group_id = creator_id

    await session.commit()

    return group


async def get_group_by_id(session: AsyncSession, id: int) -> Group:
    result = await session.execute(
        select(Group)
        .where(Group.id == id)
        .options(selectinload(Group.creator), selectinload(Group.students))
    )

    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Group not found")

    return group


async def get_group_by_title(session: AsyncSession, title: str) -> Group:
    result = await session.execute(
        select(Group)
        .where(Group.title == title)
        .options(selectinload(Group.creator), selectinload(Group.students))
    )

    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Group not found")

    return group


async def get_group_students(
    session: AsyncSession, current_user: User, group_id: int
) -> List[StudentWithDuties]:

    students_data = await get_students_data(session, current_user, group_id)
    students_with_duties = []

    for user, duties in students_data:
        duties_count = len(duties)
        last_duty = max((duty.date for duty in duties), default=None)

        student = Student(
            username=user.username,
            full_name=user.full_name,
            duties_count=duties_count,
            last_duty=last_duty,
        )

        student_duties = []
        for duty in duties:
            pydantic_duty = await duty.duty_to_pydantic(student)
            student_duties.append(pydantic_duty)

        students_with_duties.append(
            StudentWithDuties(student=student, duties=student_duties)
        )

    return students_with_duties


async def get_group_student(
    session: AsyncSession, current_user: User, group_id: int, student_id: int
) -> StudentWithDuties:

    await duty_protection(current_user, group_id)

    exists = await session.execute(
        select(User.id).where(User.id == student_id, User.group_id == group_id)
    )
    student_exists = exists.scalar_one_or_none()

    if not student_exists:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Student not found in the specified group"
        )

    result = await session.execute(
        select(User).where(User.id == student_id).options(selectinload(User.duties))
    )

    student_data = result.scalar_one()

    duties = student_data.duties
    duties_count = len(duties)
    last_duty = max((duty.date for duty in duties), default=None)

    student = Student(
        username=student_data.username,
        full_name=student_data.full_name,
        duties_count=duties_count,
        last_duty=last_duty,
    )

    duties_list = []
    for duty in duties:
        pydantic_duty = await duty.duty_to_pydantic(student)
        duties_list.append(pydantic_duty)

    return StudentWithDuties(student=student, duties=duties_list)
