from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.schemas.users import UserListOut
from app.schemas.auth import Role


class ProjectCreateIn(BaseModel):
    name: str
    description: str | None = None
    key: str | None = None


class ProjectCreateOut(ProjectCreateIn):
    id: int
    owner: UserListOut
    is_active: bool
    is_private: bool

    model_config = {
        "from_attributes": True
    }


class ProjectUpdate(BaseModel):
    name: str| None = None
    description: str | None = None
    key: str | None = None
    is_active: bool | None = None
    is_private: bool | None = None


class ProjectMemmberAddIn(BaseModel):
    user_id: int


class ProjectMemmberAddOut(ProjectMemmberAddIn):
    id: int
    project_id: int
    joined_at: datetime

    model_config = {
        "from_attributes": True
    }


class ProjectUserOut(BaseModel):
    id: int
    email: EmailStr
    role: Role
    
    model_config = {
        "from_attributes": True
    }


# class ProjectUpdateOut()
