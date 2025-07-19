from enum import Enum

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class Role(str, Enum):
    PROJECT_OWNER = "project_owner"
    PROJECT_MANAGER = "project_manager"
    DEVELOPER = "developer"
    TESTER = "tester"


class UserRegisterIn(BaseModel):
    email: EmailStr
    password: str| None = Field(min_length=6, max_length=16)
    role: Role


class UserRegisterOut(BaseModel):
    id: int
    email: EmailStr
    role: Role
    created_at: datetime
    

class UserLoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=16)


class UserLoginOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str