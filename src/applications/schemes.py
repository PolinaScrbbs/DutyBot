from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from .models import ApplicationType, ApplicationStatus


class Sending(BaseModel):
    id: int
    username: str
    full_name: str


class ApplicationForm(BaseModel):
    type: ApplicationType = ApplicationType.BECOME_ELDER
    group_id: Optional[int] = None


class BaseApplication(ApplicationForm):
    status: ApplicationStatus = ApplicationStatus.SENT


class ApplicationWithOutID(BaseApplication):
    last_update_at: datetime


class ApplicationInDB(BaseModel):
    id: int
    type: ApplicationType = ApplicationType.BECOME_ELDER
    status: ApplicationStatus = ApplicationStatus.SENT
    group_id: Optional[int] = None
    last_update_at: datetime


class ApplicationWithSending(ApplicationForm):
    id: int
    type: str
    status: str
    sending: Sending
    group_id: int
