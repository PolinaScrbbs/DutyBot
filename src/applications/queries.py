from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists

from ..user.models import User, Role
from ..user.queries import get_user_by_id
from ..group.models import Group

from .models import Application, ApplicationType, ApplicationStatus
from .schemes import (
    ApplicationForm,
    BaseApplication,
    ApplicationWithOutID,
    ApplicationInDB,
)


async def application_validate(
    session: AsyncSession, application_type: ApplicationType, group_id: Optional[int]
) -> None:

    if application_type == ApplicationType.BECOME_ELDER:
        group_id = None
    else:
        if group_id == None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "The group ID cannot be empty"
            )

    if group_id is not None:
        group_exists = await session.execute(
            select(exists().where(Group.id == group_id))
        )
        group_exists = group_exists.scalar()

        if not group_exists:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Group not found")


async def create_application(
    session: AsyncSession,
    current_user: User,
    application_data: ApplicationForm,
    sending_id: int,
) -> BaseApplication:

    application_type = ApplicationType(application_data.application_type)
    group_id = application_data.group_id

    if (
        application_type == ApplicationType.GROUP_JOIN
        and current_user.group is not None
    ):
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="You are already a member of the group"
        )

    await application_validate(session, application_type, group_id)

    application_exists = await get_application_exists(
        session, sending_id, application_type, group_id
    )

    if application_exists:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Your application has already been submitted or closed",
        )

    application = Application(
        type=application_type, sending_id=sending_id, group_id=group_id
    )

    session.add(application)
    await session.commit()


async def get_applications_list(
    session: AsyncSession,
    skip: Optional[int],
    limit: Optional[int],
    application_type: ApplicationType,
    application_status: ApplicationStatus,
    group_id: Optional[int],
) -> List[ApplicationWithOutID]:

    await application_validate(session, application_type, group_id)

    result = await session.execute(
        select(Application)
        .where(
            Application.type == application_type,
            Application.status == application_status,
            Application.group_id == group_id,
        )
        .options(
            selectinload(Application.sending).load_only(
                User.id, User.username, User.full_name
            )
        )
        .offset(skip)
        .limit(limit)
    )

    return result.scalars().all()


async def get_application_by_id(
    session: AsyncSession, application_id: int
) -> ApplicationInDB:
    result = await session.execute(
        select(Application).where(Application.id == application_id)
    )

    application = result.scalar_one_or_none()

    if application is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Application not found")

    return application


async def get_application_exists(
    session: AsyncSession,
    sending_id: int,
    application_type: ApplicationType = ApplicationType.BECOME_ELDER,
    group_id: Optional[int] = None,
) -> bool:
    result = await session.execute(
        select(
            exists().where(
                Application.sending_id == sending_id,
                Application.type == application_type,
                Application.group_id == group_id,
            )
        )
    )

    return result.scalar()


async def update_application(
    session: AsyncSession,
    current_user: User,
    application_id: int,
    update_status: ApplicationStatus,
) -> str:

    application = await get_application_by_id(session, application_id)

    if current_user.role == Role.ELDER:
        if (
            application.type == ApplicationType.BECOME_ELDER
            or current_user.group_id != application.group_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient rights to access this resource",
            )

    elif application.status != ApplicationStatus.SENT:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Cannot update application with this status"
        )

    elif update_status == ApplicationStatus.ADOPTED:
        application.status = ApplicationStatus.ADOPTED
        sending = await get_user_by_id(session, application.sending_id)
        if application.type == ApplicationType.GROUP_JOIN:
            sending.group_id = application.group_id
            msg = f"Student @{sending.username} has been accepted into the group"
        else:
            sending.role = Role.ELDER
            msg = f'Student @{sending.username} ({sending.full_name}) got the role of "Elder"'
    else:
        application.status = ApplicationStatus.REJECTED
        msg = "The application was rejected"

    await session.commit()

    return msg
