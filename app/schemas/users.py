from pydantic import BaseModel, EmailStr

from app.schemas import Role


class UserListOut(BaseModel):
    id: int
    email: EmailStr
    role: Role

    model_config = {"from_attributes": True}
