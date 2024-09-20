from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from ..user.schemes import BaseUser, Creator
from ..duty.schemes import DutyWithOutId


class GroupForm(BaseModel):
    title: str
    specialization: str
    course_number: int


class BaseGroup(GroupForm):
    creator_id: int


class GroupInDB(BaseGroup):
    created_at: datetime
    creator: Creator
    students: Optional[List[BaseUser]]

    class Config:
        from_attributes = True


class GroupResponse(BaseModel):
    message: str
    group: BaseGroup


class Student(BaseModel):
    username: str
    full_name: str
    duties_count: int
    last_duty: Optional[datetime]


class StudentWithDuties(BaseModel):
    student: Student
    duties: List[DutyWithOutId]
