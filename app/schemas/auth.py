from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegisterIn(BaseModel):
    email: EmailStr
    password: str| None = Field(min_length=6, max_length=16)
    role: str


class UserRegisterOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime
    

class UserLoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=16)


class UserLoginOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str