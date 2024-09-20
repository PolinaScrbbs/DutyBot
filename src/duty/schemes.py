from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Student(BaseModel):
    username: str
    full_name: str
    duties_count: int
    last_duty: Optional[datetime]


class DutyWithOutId(BaseModel):
    attendant: Student
    date: datetime
