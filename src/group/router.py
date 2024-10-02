from typing import List, Optional
from fastapi import Depends, APIRouter, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..auth.queries import get_current_user
from ..user.models import User, Role
from ..user import utils as ut
from ..applications.models import ApplicationStatus

from .models import Specialization
from .schemes import GroupInDB, GroupResponse, GroupForm, StudentWithDuties
from . import queries as qr
from .utils import validate_group_access
from .validators import GroupValidator

router = APIRouter()


@router.get("/specializations", response_model=List[str])
async def get_specializations(
    current_user: User = Depends(get_current_user),
):
    specializations = [specialization.value for specialization in Specialization]
    return specializations


@router.get("/groups")
async def get_groups(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    without_application: bool = False,
) -> List[GroupInDB]:
    if current_user.role != Role.ADMIN:
        if without_application:
            groups = await qr.get_group_without_user_application(
                session, current_user.id
            )
            return groups
        else:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="""
                    You do not have access to the list of groups with detailed information.\n 
                    Specify the without_application = True parameter to get a list of groups that you did not apply to join.
                """,
            )
    else:
        groups = await qr.get_groups_list(session, skip, limit)
        return groups


@router.post("/groups", response_class=Response)
async def post_group(
    group_data: GroupForm,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    await ut.elder_admin_check(current_user)

    if current_user.group_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A group with this title already exists for the current user.",
        )

    validator = GroupValidator(
        group_data.title,
        group_data.specialization,
        group_data.course_number,
        [spec.value for spec in Specialization],
        session,
    )
    await validator.validate()

    group = await qr.create_group(session, group_data, current_user.id)
    pydantic_group = await group.to_pydantic()
    msg = f"The group {group.title} was created"

    return JSONResponse(
        content=GroupResponse(
            message=msg,
            group=pydantic_group,
        ).dict(),
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/group/@{group_title}", response_model=GroupInDB)
async def get_group_by_title(
    group_title: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> GroupInDB:
    await ut.admin_check(user)
    group = await qr.get_group_by_title(session, group_title)

    return group


@router.get("/group", response_model=GroupInDB)
async def get_group_by_id(
    group_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> GroupInDB:

    await ut.user_group_exists(current_user)
    group_id = await validate_group_access(current_user, group_id)
    group = await qr.get_group_by_id(session, group_id)
    return group


@router.get("/group/students", response_model=List[StudentWithDuties])
async def get_group_students(
    group_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[StudentWithDuties]:

    await ut.user_group_exists(current_user)
    group_id = await validate_group_access(current_user, group_id)
    students = await qr.get_group_students(session, current_user.id, group_id)
    return students


@router.get("/group/student/{student_id}", response_model=StudentWithDuties)
async def get_group_student(
    student_id: int,
    group_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> StudentWithDuties:

    await ut.user_exists_by_id(session, student_id)
    await ut.user_group_exists(current_user)
    group_id = await validate_group_access(current_user, group_id)
    student = await qr.get_group_student(session, current_user, group_id, student_id)
    return student


@router.put("/group/application/{student_id}", response_class=Response)
async def application_reply(
    student_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    application_status: str = "Принят",
):
    await ut.elder_admin_check(current_user)
    await qr.application_reply(
        session, current_user, student_id, ApplicationStatus(application_status)
    )


@router.delete("/group/kick/{student_id}", response_class=Response)
async def kick_student(
    student_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Response:

    await ut.elder_admin_check(current_user)
    student = await qr.kick_student(session, current_user, student_id)
    student_first_name, student_last_name = student.full_name.split()[:2]

    return Response(
        content=f"The {student.username} ({student_first_name} {student_last_name}) has been removed from the group.\nThe student's duties have been cleared",
        status_code=status.HTTP_200_OK,
    )
