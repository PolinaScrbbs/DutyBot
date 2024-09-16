from typing import List, Optional, Tuple
from enum import Enum

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.users import Application, ApplicationType, ApplicationStatus, User, Role
from .user import get_user_by_id


async def send_application(
    session: AsyncSession, application_type: Enum, user_id: int, group_id: Optional[int]
) -> Application:
    application = Application(
        type=application_type, sending_id=user_id, group_id=group_id
    )

    try:
        session.add(application)
        await session.commit()
        return application

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        await session.close()


# async def get_group_applications(
#     session: AsyncSession, group_id: int
# ) -> List[Application]:
#     try:
#         result = await session.execute(
#             select(Application)
#             .where(
#                 Application.group_id == group_id,
#                 Application.status == ApplicationStatus.SENT,
#             )
#             .options(selectinload(Application.sending))
#         )

#         applications = result.scalars().all()
#         return applications

#     except Exception as e:
#         print(f"Error: {e}")
#         return None

#     finally:
#         await session.close()


async def get_applications(
    session: AsyncSession, application_type: ApplicationType, group_id: Optional[int]
) -> List[Application]:
    try:
        result = await session.execute(
            select(Application)
            .where(
                Application.type == application_type,
                Application.status == ApplicationStatus.SENT,
                Application.group_id == group_id,
            )
            .options(selectinload(Application.sending))
        )

        application = result.scalars().all()
        return application

    except Exception as e:
        print(f"Error: {e}")
        return None


async def get_application(
    session: AsyncSession,
    application_type: ApplicationType,
    user_id: int,
    group_id: Optional[int],
) -> Application:
    try:
        result = await session.execute(
            select(Application).where(
                Application.type == application_type,
                Application.sending_id == user_id,
                Application.group_id == group_id,
            )
        )

        application = result.scalars().one_or_none()
        return application

    except Exception as e:
        print(f"Error: {e}")
        return None


async def get_application_by_id(session: AsyncSession, application_id) -> Application:
    try:
        result = await session.execute(
            select(Application).where(Application.id == application_id)
        )

        application = result.scalars().one_or_none()
        return application

    except Exception as e:
        print(f"Error: {e}")
        return None


async def accept_application(
    session: AsyncSession, application_id: int, sending_id: int
) -> Tuple[Application, str]:
    try:
        application = await get_application_by_id(session, application_id)
        user = await get_user_by_id(session, sending_id)

        if application.group_id is not None:
            application.status = ApplicationStatus.ADOPTED
            user.group_id = application.group_id
            msg = f"Студент *@{user.username}* ({user.surname} {user.name}) *принят* в группу"
        else:
            application.status = ApplicationStatus.ADOPTED
            user.role = Role.ELDER
            msg = f'*@{user.username}* ({user.surname} {user.name}) теперь *"Староста"*'

        await session.commit()

        return application, msg

    except Exception as e:
        print(f"Error: {e}")
        await session.rollback()
        return None
    finally:
        await session.close()


async def rejected_application(
    session: AsyncSession, application_id: int, sending_id: int
) -> Tuple[Application, str]:
    try:
        application = await get_application_by_id(session, application_id)
        user = await get_user_by_id(session, sending_id)

        application.status = ApplicationStatus.REJECTED
        msg = f"Заявка *студента @{user.username}* ({user.surname} {user.name}) *отклонена*"

        await session.commit()

        return application, msg

    except Exception as e:
        print(f"Error: {e}")
        await session.rollback()
        return None
    finally:
        await session.close()
