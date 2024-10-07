from typing import List, Optional, Union
from pydantic import BaseModel
from datetime import datetime

class BaseUser(BaseModel):
    id: int
    role: str
    username: str
    full_name: str
    group_id: Optional[int] = None
    avatar_url: Optional[str]
    created_at: Union[datetime, str]


class UserCreate(BaseModel):
    username: str
    password: str
    confirm_password: str
    full_name: str
    avatar_url: Optional[str] = None


class UserUpdate(BaseUser):
    hashed_password: Optional[str] = None


class TokenInDB(BaseModel):
    id: int
    token: str
    user_id: int


class Group(BaseModel):
    title: str
    specialization: str
    course_number: int
    creator_id: int


class UserInDB(BaseUser):
    token: Optional[List[TokenInDB]] = None
    created_group: Optional[List[Group]] = None
    group: Optional[Group] = None

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


class UserResponse(BaseModel):
    message: str
    user: BaseUser
