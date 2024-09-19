from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists

from ..user.models import User
from ..group.models import Group

from .models import Application, ApplicationType, ApplicationStatus
from .schemes import ApplicationForm, BaseApplication, ApplicationInDB

async def get_applications_list(
    session: AsyncSession,
    skip: Optional[int], 
    limit: Optional[int],
    type: ApplicationType,
    status: ApplicationStatus
) -> List[ApplicationInDB]:
    
    result = await session.execute(
        select(Application)
        .where(
            Application.type==type,
            Application.status==status
        )
        .options(
            selectinload(Application.sending)
            .load_only(
                User.id,
                User.username,
                User.full_name
            )
        )
        .offset(skip)
        .limit(limit)
    )

    return result.scalars().all()

async def get_application_exists(
    session: AsyncSession,
    sending_id: int,
    application_type: ApplicationType = ApplicationType.BECOME_ELDER,
    group_id: int = None
) -> bool:
    result = await session.execute(
        select(
            exists()
            .where(
                Application.sending_id==sending_id,
                Application.type==application_type,
                Application.group_id==group_id
            )
        )
    )

    return result.scalar()

async def create_application(
    session: AsyncSession, 
    application_data: ApplicationForm,
    sending_id: int
) -> BaseApplication:
    
    application_type = ApplicationType(application_data.type)
    group_id = application_data.group_id

    if application_type == ApplicationType.BECOME_ELDER:
        group_id = None
    else:
        if group_id == None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "The group ID cannot be empty"
            )

    if group_id is not None:
        group_exists = await session.execute(
            select(exists().where(Group.id==group_id))
        )
        group_exists = group_exists.scalar()
        print(group_id, group_exists)

        if not group_exists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
    
    application_exists = await get_application_exists(
        session, sending_id, application_type, group_id
    )

    if application_exists:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Your application has already been submitted or closed"
        )

    application = Application(
        type=application_type,
        sending_id=sending_id,
        group_id=group_id
    )

    session.add(application)
    await session.commit()

