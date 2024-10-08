from typing import List, Optional
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..auth.queries import get_current_user
from ..user.models import User, Role
from ..user import utils as ut

from .models import ApplicationType, ApplicationStatus
from . import queries as qr
from .schemes import ApplicationForm, ApplicationWithSending


router = APIRouter()


@router.post("/applications", response_class=JSONResponse)
async def post_application(
    application_data: ApplicationForm,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> JSONResponse:

    await qr.create_application(
        session, current_user, application_data, sending_id=current_user.id
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "The application has been sent"},
    )


@router.get("/applications", response_model=List[ApplicationWithSending])
async def get_applications(
    skip: int = 0,
    limit: int = 10,
    application_type: ApplicationType = ApplicationType.BECOME_ELDER,
    application_status: ApplicationStatus = ApplicationStatus.SENT,
    group_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[ApplicationWithSending]:

    await ut.elder_admin_check(current_user)
    await ut.user_group_exists(current_user)

    # if current_user.role == Role.ELDER:
    #     if group_id is None:
    #         group_id = current_user.group_id
    #     else:
    #         raise HTTPException(
    #             status.HTTP_403_FORBIDDEN,
    #             detail="You cannot use a request with the user_id parameter"
    #         )

    applications = await qr.get_applications_list(
        session, skip, limit, application_type, application_status, group_id
    )

    if not applications:
        raise HTTPException(
            status.HTTP_204_NO_CONTENT, detail="List of applications is empty"
        )

    print(applications)
    return applications


@router.get("/application/{application_id}", response_model=ApplicationWithSending)
async def get_application_by_id(
    application_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ApplicationWithSending:

    await ut.elder_admin_check(current_user)
    await ut.user_group_exists(current_user)
    application = await qr.get_application_by_id(session, application_id)

    if current_user.role == Role.ELDER:
        if application.group_id != current_user.group_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient rights to access this resource",
            )

    return application


@router.put("/application/{application_id}")
async def update_application(
    application_id: int,
    update_status: ApplicationStatus = ApplicationStatus.ADOPTED,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await ut.elder_admin_check(current_user)
    await ut.user_group_exists(current_user)
    msg = await qr.update_application(
        session, current_user, application_id, ApplicationStatus(update_status)
    )

    return msg
