from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.schemas import Role


class UserListOut(BaseModel):
    id: int
    email: EmailStr
    role: Role
    created_at: datetime

    model_config = {
        "from_attributes": True
    }