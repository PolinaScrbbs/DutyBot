from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import exists
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.models import User, Role
from ..user.queries import get_user_by_id
from ..applications.models import Application, ApplicationType, ApplicationStatus
from ..duty.models import Duty
from ..duty.queries import get_users_data

from .models import Group, Specialization
from .schemes import GroupForm, GroupFormsInfo, BaseGroup, GroupInDB, Student, StudentWithDuties
from .utils import check_empty_groups, check_group_exists


async def get_groups_list(
    session: AsyncSession, skip: Optional[int], limit: Optional[int]
) -> List[GroupInDB]:

    result = await session.execute(
        select(Group)
        .options(
            selectinload(Group.creator).load_only(
                User.id, User.role, User.username, User.full_name
            ),
            selectinload(Group.students),
        )
        .offset(skip)
        .limit(limit)
    )

    groups = result.scalars().all()
    await check_empty_groups(groups)
    return groups


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
    await check_group_exists(group)
    return group


async def get_group_by_title(session: AsyncSession, title: str) -> Group:
    result = await session.execute(
        select(Group)
        .where(Group.title == title)
        .options(selectinload(Group.creator), selectinload(Group.students))
    )

    group = result.scalar_one_or_none()
    await check_group_exists(group)
    return group


async def get_group_without_user_application(
    session: AsyncSession, user_id: int
) -> List[GroupForm]:

    result = await session.execute(
        select(Group.id, Group.title, Group.specialization, Group.course_number).where(
            ~exists(
                select(Application.id).where(
                    Application.type == ApplicationType.GROUP_JOIN,
                    Application.sending_id == user_id,
                    Application.group_id == Group.id,
                )
            )
        )
    )

    groups = result.fetchall()

    group_forms = [
        GroupFormsInfo(
            id=group.id,
            title=group.title,
            specialization=group.specialization,
            course_number=group.course_number,
        )
        for group in groups
    ]

    return group_forms


async def get_group_students(
    session: AsyncSession, current_user: User, group_id: int
) -> List[StudentWithDuties]:

    students_data = await get_users_data(session, current_user, group_id)
    students_with_duties = []

    for user, duties in students_data:
        duties_count = len(duties)
        last_duty = max((duty.date for duty in duties), default=None)

        student = Student(
            id=user.id,
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

    if current_user.role == Role.ELDER:
        exists = await session.execute(
            select(User.id).where(User.id == student_id, User.group_id == group_id)
        )
        student_exists = exists.scalar_one_or_none()

        if not student_exists:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="There are not enough rights to receive information from a student from another group",
            )

    result = await session.execute(
        select(User).where(User.id == student_id).options(selectinload(User.duties))
    )

    student_data = result.scalar_one()

    duties = student_data.duties
    duties_count = len(duties)
    last_duty = max((duty.date for duty in duties), default=None)

    student = Student(
        id=student_data.id,
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


async def application_reply(
    session: AsyncSession,
    current_user: User,
    user_id: int,
    application_status: ApplicationStatus,
):
    user = await get_user_by_id(session, user_id)

    if current_user == user:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="You cannot accept yourself"
        )
    if current_user.role != Role.ELDER:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Only the head of the group can accept a student",
        )

    if current_user.group_id != user.group_id:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="This student is not from your group"
        )

    result = await session.execute(
        select(Application).where(
            Application.type == ApplicationType.GROUP_JOIN,
            Application.sending_id == user.id,
            Application.group_id == current_user.group_id,
        )
    )

    application = result.scalar_one_or_none()

    if application is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="The user's entry application was not found",
        )

    user.group_id = current_user.group_id
    application.status = application_status
    await session.commit()


async def kick_student(session: AsyncSession, current_user: User, user_id: int):
    user = await get_user_by_id(session, user_id)

    if current_user == user:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="You can't kick yourself")

    if current_user.group_id != user.group_id:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="This student is not from your group"
        )

    user.group_id = None
    await session.flush()

    result = await session.execute(select(Duty).where(Duty.attendant_id == user.id))
    user_duties = result.scalars().all()

    for duty in user_duties:
        await session.delete(duty)

    await session.commit()
