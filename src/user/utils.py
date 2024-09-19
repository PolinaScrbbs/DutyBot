from fastapi import HTTPException, status

from .models import User, Role


async def admin_check(user: User):
    if user.role is not Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient rights to access this resource",
        )


async def elder_check(user: User):
    if user.role is Role.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient rights to access this resource",
        )
