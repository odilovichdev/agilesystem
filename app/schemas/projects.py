from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.schemas.users import UserListOut
from app.schemas.auth import Role



class ProjectOwnerNasted(BaseModel):
    id: int
    email: EmailStr
    role: Role
    fullname: str | None = None
    avatar: str | None = None


class ProjectCreateRequest(BaseModel):
    name: str
    description: str | None = None
    is_private: bool | None = False


class ProjectInviteRequest(BaseModel):
    user_id: int


class ProjectKickRequest(BaseModel):
    user_id: int


class ProjectMemmberResponse(BaseModel):
    id: int
    user: ProjectOwnerNasted
    joined_at: datetime


class ProjectResponse(BaseModel):
    id: int
    name: str
    key: str
    description: str | None = None
    owner: ProjectOwnerNasted

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Project 1",
                "key": "P1",
                "description": "Project description",
                "owner": {
                    "id": 1,
                    "email": "bY9vD@example.com",
                    "fullname": "John Doe",
                }
            }
        }
    }


class ProjectUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    is_private: bool | None = None

