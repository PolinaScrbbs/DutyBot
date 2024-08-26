from typing import List

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.users import Role, Specialization, Group, Application, User
from .user import get_user_by_username, get_user_by_id

async def create_group(session: AsyncSession, title: str, specialization: Specialization, course_number: int, creator_username: str) -> Group:
    user = await get_user_by_username(session, creator_username)

    group = Group(
        title = title,
        specialization = specialization,
        course_number = course_number,
        creator_id = user.id
    )

    try:
        session.add(group)
        await session.commit()

        user.group_id = group.id
        await session.commit()

        return group
    
    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        await session.close()

async def get_groups(session: AsyncSession) -> List[Group]:
    try:
        result = await session.execute(
            select(Group)
        )

        groups = result.scalars().all()

        return groups
    
    except Exception as e:
        print(f"Error: {e}")
        return []
    
async def get_group_by_id(session: AsyncSession, id: int) -> Group:
    try:
        result = await session.execute(
            select(Group).where(Group.id == id)
        )
        group = result.scalars().one_or_none()

        return group
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
async def get_group_by_id_with_students_and_applications(session: AsyncSession, group_id: int, user_id: int) -> Group:
    try:
        result = await session.execute(
            select(Group).where(Group.id == group_id).options(
                selectinload(Group.students.and_(User.id != user_id)),
                selectinload(Group.applications)
            )
        )
        group = result.scalars().one_or_none()

        return group
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
async def get_group_by_title(session: AsyncSession, title: str) -> Group:
    try:
        result = await session.execute(
            select(Group).where(Group.title == title)
        )
        group = result.scalars().one_or_none()

        return group
    
    except Exception as e:
        print(f"Error: {e}")
        return None

async def get_groups_without_application_from_user(session: AsyncSession, user_id) -> List[Group]:
    try:
        groups = await get_groups(session)

        groups_with_application = await session.execute(
            select(Application.group_id).where(Application.sending_id == user_id)
            )
        groups_with_application_ids = groups_with_application.scalars().all()

        groups_without_application = [group for group in groups if group.id not in groups_with_application_ids]

        return groups_without_application
    
    except Exception as e:
        print(f"Error: {e}")
        return []
    
    finally:
        await session.close()

async def get_specialization(text: str) -> Specialization:
    for spec in Specialization:
        if spec.value == text:
            return spec
    raise ValueError(f"Specialization с текстом '{text}' не найдена.")

async def kick_student(session: AsyncSession, student_id: int) -> User:
    try:
        student = await get_user_by_id(session, student_id)
        student.group_id = None
        await session.commit()

        return student
    
    except Exception as e:
        print(f"Error: {e}")
        await session.rollback()
    finally:
        await session.close()

async def get_students(session: AsyncSession, group_id: int) -> List[User]:
    try:
        result = await session.execute(
            select(User).where(
                    User.group_id == group_id,
                    User.role == Role.STUDENT
                ).options(
                    selectinload(User.duties)
                )
        )

        students = result.scalars().all()
        return students

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await session.close()
    