from typing import List, Optional, Sequence, Any
from fastapi import HTTPException, status
from sqlalchemy import exists, func, update, delete, Row, RowMapping
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.models import User, Role
from ..user.queries import get_user_by_id
from ..applications.models import Application, ApplicationType, ApplicationStatus
from ..duty.models import Duty
from ..duty.schemes import BaseDuty

from .models import Group, Specialization, GetGroupFilters
from .schemes import GroupInDB, GroupUpdate, Student, StudentWithDuties, GroupForm
from .utils import check_empty_groups, check_group_exists


async def get_groups_list(
    session: AsyncSession,
    skip: Optional[int],
    limit: Optional[int],
    filters: Optional[GetGroupFilters] = None,
) -> Sequence[Row[Any] | RowMapping | Any]:
    stmt = select(Group).options(
        selectinload(Group.creator).load_only(
            User.id, User.role, User.username, User.full_name, User.avatar_url
        ),
        selectinload(Group.students),
    )

    if filters:
        if filters.course_number is not None:
            stmt = stmt.where(Group.course_number == filters.course_number)
        if filters.specialization is not None:
            stmt = stmt.where(Group.specialization == filters.specialization)

    stmt = stmt.offset(skip).limit(limit)

    result = await session.execute(stmt)
    groups = result.scalars().all()
    await check_empty_groups(groups)
    return groups


async def create_group(
    session: AsyncSession, group_create: GroupForm, creator_id: int
) -> Group:
    group = Group(
        title=group_create.title,
        specialization=Specialization(group_create.specialization),
        course_number=group_create.course_number,
        creator_id=creator_id,
    )

    session.add(group)
    await session.flush()

    user = await get_user_by_id(session, creator_id)
    user.group_id = group.id

    await session.commit()
    await session.refresh(group)
    return group


async def get_group_by_creator_id(session: AsyncSession, creator_id: int) -> Group:
    try:
        result = await session.execute(
            select(Group).where(Group.creator_id == creator_id)
        )
        group = result.scalar_one()
        return group
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Группа не найдена")


async def update_group(
    session: AsyncSession, creator_id: int, update_form: GroupUpdate
) -> Group:
    group = await get_group_by_creator_id(session, creator_id)
    update_data = update_form.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(group, key, value)

    await session.commit()
    await session.refresh(group)

    return group


async def delete_group(session: AsyncSession, creator_id: int) -> None:
    result = await session.execute(select(Group).where(Group.creator_id == creator_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    group_id = group.id

    await session.execute(
        update(User).where(User.group_id == group_id).values(group_id=None)
    )

    await session.execute(delete(Application).where(Application.group_id == group_id))

    await session.delete(group)
    await session.commit()


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
    session: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    filters: Optional[GetGroupFilters] = None,
) -> Sequence[Group]:
    stmt = (
        select(Group)
        .options(
            selectinload(Group.creator),
            selectinload(Group.students),
        )
        .where(
            ~exists(
                select(Application.id).where(
                    Application.type == ApplicationType.GROUP_JOIN,
                    Application.sending_id == user_id,
                    Application.group_id == Group.id,
                )
            )
        )
    )

    if filters:
        if filters.course_number is not None:
            stmt = stmt.where(Group.course_number == filters.course_number)
        if filters.specialization is not None:
            stmt = stmt.where(Group.specialization == filters.specialization)

    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    groups = result.scalars().all()
    await check_empty_groups(groups)
    return groups


async def get_group_students(
    session: AsyncSession, current_user_id: int, group_id: Optional[int] = None
) -> List[StudentWithDuties]:
    result = await session.execute(
        select(
            User,
            func.count(Duty.id).label("duties_count"),
            func.max(Duty.date).label("last_duty"),
        )
        .join(Duty, Duty.attendant_id == User.id, isouter=True)
        .where(User.id != current_user_id, User.group_id == group_id)
        .options(selectinload(User.duties))
        .group_by(User.id)
    )

    rows = result.all()

    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="В группе нет студентов")

    students_with_duties = []
    for row in rows:
        user = row[0]
        duties_count = row.duties_count
        last_duty = row.last_duty

        duties = [BaseDuty(id=duty.id, date=duty.date) for duty in user.duties]

        student_with_duties = StudentWithDuties(
            student=Student(
                id=user.id,
                username=user.username,
                full_name=await user.formatted_full_name(),
                duties_count=duties_count,
                last_duty=last_duty.strftime("%Y-%m-%d") if last_duty else "-",
            ),
            duties=duties,
        )

        students_with_duties.append(student_with_duties)

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
                detail="Недостаточно прав для получения информации о студенте из другой группы",
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

    duties = [BaseDuty(id=duty.id, date=duty.date) for duty in student_data.duties]

    return StudentWithDuties(student=student, duties=duties)


async def application_reply(
    session: AsyncSession,
    current_user: User,
    user_id: int,
    application_status: ApplicationStatus,
):
    user = await get_user_by_id(session, user_id)

    if current_user == user:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="Нельзя принять самого себя"
        )
    if current_user.role != Role.ELDER:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Только староста может принять студента",
        )

    if current_user.group_id != user.group_id:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Этот студент не из вашей группы",
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
            detail="Заявка студента на вступление в группу не найдена",
        )

    user.group_id = current_user.group_id
    application.status = application_status
    await session.commit()


async def kick_student(session: AsyncSession, current_user: User, user_id: int):
    user = await get_user_by_id(session, user_id)

    if current_user == user:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="Нельзя исключить самого себя"
        )

    if current_user.group_id != user.group_id:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Этот студент не из вашей группы",
        )

    user.group_id = None
    await session.flush()

    result = await session.execute(select(Duty).where(Duty.attendant_id == user.id))
    user_duties = result.scalars().all()

    for duty in user_duties:
        await session.delete(duty)

    await session.commit()

    return user
