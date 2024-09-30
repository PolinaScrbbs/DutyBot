from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from ..duty.schemes import BaseDuty, Student

from ..user.schemes import BaseUser


class NullGroup(BaseModel):
    id: int


class GroupForm(BaseModel):
    title: str
    specialization: str
    course_number: int


class GroupFormsInfo(GroupForm, NullGroup):
    pass


class BaseGroup(GroupFormsInfo):
    creator_id: int


class Creator(BaseModel):
    id: int
    role: str
    username: str
    full_name: str


class GroupInDB(GroupFormsInfo):
    created_at: datetime
    creator: Creator
    students: Optional[List[BaseUser]]

    class Config:
        from_attributes = True


class GroupResponse(BaseModel):
    message: str
    group: BaseGroup

class StudentWithDuties(BaseModel):
    student: Student
    duties: List[BaseDuty]
