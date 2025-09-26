from pydantic import BaseModel, EmailStr

from app.enums import Role


class NotificationNastedUser(BaseModel):
    email: EmailStr
    role: Role

    model_config = {"from_attributes": True}


class NotificationListReponse(BaseModel):
    id: int
    message: str
    sender: NotificationNastedUser