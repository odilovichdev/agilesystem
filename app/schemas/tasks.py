from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.enums import Priority, Role, Status

class TaskUserNested(BaseModel):
    id: int
    email: EmailStr
    role: Role

    model_config = {"from_attributes": True}


class TaskCreateRequest(BaseModel):
    project_key: str
    summary: str
    description: str | None = None
    priority: Priority
    due_date: datetime


class TaskAddDeveloperRequest(BaseModel):
    user_id: int


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
    assignee: TaskUserNested | None = None
    reporter: TaskUserNested
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
    assignee: TaskListUserNested | None = None
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
