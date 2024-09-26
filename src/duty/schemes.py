from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel


class BaseStudent(BaseModel):
    id: int
    username: str
    full_name: str


class Student(BaseStudent):
    duties_count: int
    last_duty: Optional[Union[datetime, str]]


class DutyWithOutId(BaseModel):
    attendant: Student
    date: Union[datetime, str]
