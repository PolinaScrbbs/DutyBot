from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Attendant(BaseModel):
    username: str
    full_name: str
    duties_count: int
    last_duty: Optional[datetime]


class DutyWithOutId(BaseModel):
    attendant: Attendant
    date: datetime


class AttendantWithDuties(BaseModel):
    attendant: Attendant
    duties: List[DutyWithOutId]
