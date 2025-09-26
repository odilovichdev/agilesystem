from pydantic import BaseModel, EmailStr

from app.schemas import Role


class UserListResponse(BaseModel):
    id: int
    email: EmailStr
    role: Role

    model_config = {"from_attributes": True}


__all__ = ["UserListResponse"]
