from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from .models import ApplicationType, ApplicationStatus

class Sending(BaseModel):
    id: int
    username: str
    full_name: str

class ApplicationForm(BaseModel):
    type: str = ApplicationType.BECOME_ELDER
    group_id: Optional[int] = None

class BaseApplication(ApplicationForm):
    status: str = ApplicationStatus.SENT

class ApplicationInDB(BaseApplication):
    last_update_at: datetime

class ApplicationWithSending(ApplicationForm):
    id: int
    type: str
    status: str
    sending: Sending
    group_id: int