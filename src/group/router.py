from typing import List, Optional
from fastapi import Depends, APIRouter, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..auth.queries import get_current_user
from ..user.models import User, Role
from ..user import utils as ut

from .models import Specialization
from .schemes import BaseGroup, GroupInDB, GroupResponse, GroupForm, StudentWithDuties
from . import queries as qr
from .utils import validate_group_access
from .validators import GroupValidator

router = APIRouter()


@router.get("/groups", response_model=List[GroupInDB])
async def get_groups(
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    without_application: bool = False
) -> List[GroupInDB]:
    if current_user.role != Role.admin:
        if without_application:
            groups = await qr.get_group_without_user_application(session, current_user.id)
        else:
            HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail='''
                    You do not have access to the list of groups with detailed information.\n 
                    Specify the without_application = True parameter to get a list of groups that you did not apply to join.
                '''
            )
    else:
        groups = await qr.get_groups_list(session, skip, limit)
        return groups


@router.post("/groups", response_model=GroupResponse)
async def post_group(
    group_data: GroupForm,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> GroupResponse:
    await ut.elder_check(current_user)

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

    return GroupResponse(
        message=f'The group "{group.title}" was created by {current_user.username}',
        group=await group.to_pydantic(),
    )


@router.get("/group/@{group_title}", response_model=BaseGroup)
async def get_group_by_title(
    group_title: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> GroupInDB:
    await ut.admin_check(user)
    group = await qr.get_group_by_title(session, group_title)

    return await group.to_pydantic()


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
    students = await qr.get_group_students(session, current_user, group_id)
    return students


@router.get("/group/student/{student_id}", response_model=StudentWithDuties)
async def get_group_student(
    student_id: int,
    group_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> StudentWithDuties:

    await ut.user_group_exists(current_user)
    group_id = await validate_group_access(current_user, group_id)
    student = await qr.get_group_student(session, current_user, group_id, student_id)
    return student

@router.delete("/group/kick/{student_id}", response_class=Response)
async def kick_student(
    student_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Response:
    
    await ut.elder_check(current_user)
    await qr.kick_student(session, current_user, student_id)

    return Response(
        content="The student has been removed from the group.\nThe student's duties have been cleared",
        status_code=status.HTTP_200_OK
    )
