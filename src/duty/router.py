from typing import List, Optional
from fastapi import Depends, APIRouter, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..auth.queries import get_current_user
from ..user.models import User
from ..user import utils as ut

from . import queries as qr
from .schemes import DutyWithOutId

router = APIRouter()


@router.post("/duties", response_class=Response)
async def post_duties(
    attendant_ids: List[int] = [1, 2],
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Response:

    await ut.elder_check(user)
    await qr.post_duties(session, user, attendant_ids)
    return Response("The duties are set", status.HTTP_201_CREATED)


@router.get("/duties/{group_id}", response_model=List[DutyWithOutId])
async def get_group_duties(
    group_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> List[DutyWithOutId]:

    duties = await qr.get_group_duties(session, user, group_id)
    return duties
