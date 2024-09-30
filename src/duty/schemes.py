from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel


class BaseDuty(BaseModel):
    id: int
    date: Union[datetime, str]

class BaseStudent(BaseModel):
    id: int
    username: str
    full_name: str


class Student(BaseStudent):
    duties_count: Optional[int] = None
    last_duty: Optional[Union[datetime, str]] = None


class DutyWithOutId(BaseModel):
    attendant: Student
    date: Union[datetime, str]
