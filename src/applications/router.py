from typing import List, Optional
from fastapi import Depends, APIRouter, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..auth.queries import get_current_user
from ..user.models import User
from ..user import utils as ut

from .models import ApplicationType, ApplicationStatus
from . import queries as qr
from .schemes import ApplicationInDB, ApplicationForm

router = APIRouter(prefix="/applications")


@router.get("/", response_model=List[ApplicationInDB])
async def get_applications(
    skip: int = 0,
    limit: int = 10,
    application_type: ApplicationType = ApplicationType.BECOME_ELDER,
    application_status: ApplicationStatus = ApplicationStatus.SENT,
    group_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> List[ApplicationInDB]:

    await ut.admin_check(user)
    applications = await qr.get_applications_list(
        session, skip, limit, application_type, application_status, group_id
    )

    if applications == []:
        raise HTTPException(status.HTTP_200_OK, detail="List of applications is empty")

    return applications


@router.post("/", response_class=Response)
async def post_application(
    application_data: ApplicationForm,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Response:
    await qr.create_application(session, application_data, sending_id=user.id)
    return Response(
        status_code=status.HTTP_201_CREATED, content="The application has been sent"
    )
