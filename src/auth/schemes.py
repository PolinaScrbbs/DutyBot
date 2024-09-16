from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..group.schemes import GroupInDB

class BaseUser(BaseModel):
    role: str
    username: str
    full_name: str
    group_id: Optional[int] = None
    created_at: datetime

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str

class UserUpdate(BaseUser):
    hashed_password: Optional[str] = None

class TokenInDB(BaseModel):
    id: int
    token: str
    user_id: int

class UserInDB(BaseUser):
    id: int
    token: Optional[List[TokenInDB]] = None
    created_group: Optional[List[GroupInDB]] = None
    group: Optional[GroupInDB] = None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    message: str
    user: BaseUser