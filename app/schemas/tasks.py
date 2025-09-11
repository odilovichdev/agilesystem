from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.enums import Priority, Role, Status


class TaskCreateRequest(BaseModel):
    project_key: str
    summary: str
    description: str | None = None
    status: Status
    priority: Priority
    assignee_id: int
    due_date: datetime


class TaskListProjectNested(BaseModel):
    key: str


class TaskListUserNested(BaseModel):
    id: int
    email: EmailStr
    role: Role
    fullname: str | None


class TaskListResponse(BaseModel):
    id: int
    project: TaskListProjectNested
    key: str
    summary: str
    status: Status
    priority: Priority


class TaskDetailResponse(BaseModel):
    id: int
    project: TaskListProjectNested
    key: str
    summary: str
    status: Status
    priority: Priority
    assignee: TaskListUserNested
    reporter: TaskListUserNested
    due_date: datetime


class TaskUpdateRequest(BaseModel):
    status: Status | None = None
    summary: str | None = None
    description: str | None = None
    priority: Priority | None = None
    assignee_id: int | None = None
    due_date: datetime | None = None


class TaskMoveRequest(BaseModel):
    status: Status
