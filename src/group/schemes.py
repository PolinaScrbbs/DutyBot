from datetime import datetime
from pydantic import BaseModel

class GroupInDB(BaseModel):
    title: str
    specialization: str
    course_number: int
    creator_id: int
    created_at: datetime