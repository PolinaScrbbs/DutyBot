from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Creator(BaseModel):
    role: str
    username: str
    full_name: str

class BaseUser(Creator):
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

class Group(BaseModel):
    title: str
    specialization: str
    course_number: int
    creator_id: int

class UserInDB(BaseUser):
    id: int
    token: Optional[List[TokenInDB]] = None
    created_group: Optional[List[Group]] = None
    group: Optional[Group] = None

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

class UserResponse(BaseModel):
    message: str
    user: BaseUser