from typing import List, Optional
from fastapi import Depends, APIRouter, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..auth.queries import get_current_user
from ..user.models import User, Role
from ..user import utils as ut

from . import queries as qr


router = APIRouter(prefix="/duties")


@router.post("/", response_class=Response)
async def post_duties(
    attendant_ids: List[int] = [1, 2],
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
) -> Response:
    print(attendant_ids)
    await ut.elder_check(user)
    await qr.post_duties(session, user, attendant_ids)
    return Response(
        "The duties are set",
        status.HTTP_201_CREATED
    )