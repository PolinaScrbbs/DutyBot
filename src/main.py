from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from .auth.router import router as authRouter
from .user.router import router as userRouter
from .group.router import router as groupRouter

app = FastAPI()

app.include_router(authRouter, tags=["auth"])
app.include_router(userRouter, tags=["users"])
app.include_router(groupRouter, tags=["groups"])

