from enum import Enum
from datetime import datetime

from pydantic import BaseModel


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreateIn(BaseModel):
    key: str
    summary: str
    description: str | None = None
    priority: Priority = "low"
    due_date: datetime

    project_id: int
    status_id: int
    assignee_id: int


class TaskCreateOut(TaskCreateIn):
    ...

    