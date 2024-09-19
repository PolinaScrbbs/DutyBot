from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists

from ..user.models import User
from ..user.queries import get_user_by_id
from ..group.models import Group

from .models import Application, ApplicationType, ApplicationStatus
from .schemes import (
    ApplicationForm,
    BaseApplication,
    ApplicationWithOutID,
    ApplicationInDB,
)


async def create_application(
    session: AsyncSession, application_data: ApplicationForm, sending_id: int
) -> BaseApplication:

    application_type = ApplicationType(application_data.type)
    group_id = application_data.group_id

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
        print(group_id, group_exists)

        if not group_exists:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Group not found")


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

    return


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
    application_id: int,
    status: ApplicationStatus,
):
    application = await get_application_by_id(session, application_id)
    user = await get_user_by_id(session, application.sending_id)
