from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel

from .models import ApplicationType, ApplicationStatus


class Sending(BaseModel):
    id: int
    username: str
    full_name: str


class ApplicationForm(BaseModel):
    type: ApplicationType = ApplicationType.BECOME_ELDER
    group_id: Optional[int] = None


class ApplicationWithSending(BaseModel):
    id: int
    type: ApplicationType
    status: ApplicationStatus
    group_id: Optional[int]
    sending: Sending
    last_update_at: Union[datetime, str]
