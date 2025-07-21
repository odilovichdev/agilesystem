from enum import Enum
from datetime import datetime

from pydantic import BaseModel

from app.schemas.users import UserListOut
from app.schemas.status import StatusCreateOut
from app.schemas.projects import ProjectCreateOut


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreateIn(BaseModel):
    key: str
    summary: str
    description: str | None = None
    priority: Priority = Priority.LOW.value
    due_date: datetime

    project_id: int
    status_id: int
    assignee_id: int



class TaskCreateOut(BaseModel):
    key: str
    summary: str
    description: str | None = None
    priority: Priority = Priority.LOW.value
    due_date: datetime

    project: ProjectCreateOut
    status: StatusCreateOut
    assignee: UserListOut

    model_config = {
        "from_attributes": True
    }

    