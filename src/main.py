from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from .auth.users import router

app = FastAPI()

app.include_router(router, tags=["users"])

