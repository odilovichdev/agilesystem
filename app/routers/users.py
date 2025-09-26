from typing import List

from fastapi import APIRouter

from app.dependencies import db_dep
from app.models import User
from app.schemas import UserListResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserListResponse])
async def user_list(db: db_dep):
    users = db.query(User).all()

    return users
