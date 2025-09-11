from pydantic import BaseModel, EmailStr, Field

from app.enums import Role


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str | None = Field(min_length=6, max_length=16)
    role: Role


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
