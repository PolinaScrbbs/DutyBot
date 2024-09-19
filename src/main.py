from fastapi import FastAPI

from .auth.router import router as authRouter
from .user.router import router as usersRouter
from .group.router import router as groupsRouter
from .applications.router import router as applicationsRouter

app = FastAPI(
    title="Duty Bot Api", 
    description="API for Telegram Bot DutyBot",
    version="0.0.7"
)

app.include_router(authRouter, tags=["auth"])
app.include_router(usersRouter, tags=["users"])
app.include_router(groupsRouter, tags=["groups"])
app.include_router(applicationsRouter, tags=["applications"])

