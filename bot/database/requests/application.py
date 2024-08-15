from typing import List, Optional
from enum import Enum

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.users import Application

async def send_application(session: AsyncSession, application_type: Enum, user_id: int, group_id: Optional[int]) -> Application:
    application = Application(
        type = application_type,
        sending_id = user_id,
        group_id = group_id
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

async def get_group_applications(session: AsyncSession, group_id: int) -> List[Application]:
    try:
        result = await session.execute(
            select(Application).where(Application.group_id == group_id).options(
                selectinload(Application.sending)
            )
        )

        applications = result.scalars().all()
        return applications

    except Exception as e:
        print(f"Error: {e}")
        return None
    
    finally:
        await session.close()

async def get_application(session: AsyncSession, application_type: Enum, user_id: int, group_id: Optional[int]) -> Application:
    try:
        result = await session.execute(
            select(Application).where(
                Application.type==application_type, 
                Application.sending_id==user_id, 
                Application.group_id==group_id
            )
        )

        application = result.scalars().one_or_none()
        return application
    
    except Exception as e:
        print(f"Error: {e}")
        return None