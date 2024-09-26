from typing import List, Optional
from fastapi import Depends, APIRouter, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..auth.queries import get_current_user
from ..user.models import User
from ..user import utils as ut
from ..group.utils import validate_group_access

from . import queries as qr
from .schemes import BaseStudent, DutyWithOutId

router = APIRouter()


@router.post("/duties", response_class=Response)
async def post_duties(
    attendant_ids: List[int] = [1, 2],
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Response:

    await ut.elder_check(current_user)
    await ut.user_group_exists(current_user)
    await qr.post_duties(session, current_user, attendant_ids)
    return Response("The duties are set", status.HTTP_201_CREATED)


@router.get("/duties", response_model=List[DutyWithOutId])
async def get_group_duties(
    group_id: Optional[int] = None,
    attendant_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[DutyWithOutId]:

    await ut.user_group_exists(current_user)
    group_id = await validate_group_access(current_user, group_id)
    duties = await qr.get_group_duties(session, current_user, group_id, attendant_id)
    return duties


@router.get("/attendants", response_model=List[BaseStudent])
async def get_attendatns(
    group_id: Optional[int] = None,
    missed_students_id: Optional[List[int]] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[BaseStudent]:

    await ut.user_group_exists(current_user)
    group_id = await validate_group_access(current_user, group_id)
    attendants = await qr.get_group_attendants(session, group_id, missed_students_id)
    return attendants
