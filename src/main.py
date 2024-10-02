from fastapi import FastAPI

from .auth.router import router as authRouter
from .user.router import router as usersRouter
from .group.router import router as groupsRouter
from .applications.router import router as applicationsRouter
from .duty.router import router as dutiesRouter

app = FastAPI(
    title="Duty Bot Api", description="API for Telegram Bot DutyBot", version="1.0.0"
)

app.include_router(authRouter, tags=["Auth"])
app.include_router(usersRouter, tags=["Users"])
app.include_router(groupsRouter, tags=["Groups"])
app.include_router(applicationsRouter, tags=["Applications"])
app.include_router(dutiesRouter, tags=["Duties"])
