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


class TaskListOut(BaseModel):
    id: int
    key: str
    summary: str
    description: str | None = None
    priority: Priority = Priority.LOW.value
    due_date: datetime

    project: ProjectCreateOut
    status: StatusCreateOut
    assignee: UserListOut
    reporter: UserListOut

    model_config = {
        "from_attributes": True
    }


class TaskEditIn(BaseModel):
    key: str | None = None
    summary: str | None = None
    description: str | None = None
    due_date: datetime | None = None


class TaskEditOut(TaskCreateIn):
    ...


class TaskDetailOut(TaskListOut):
    ...