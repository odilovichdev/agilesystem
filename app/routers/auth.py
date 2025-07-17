from fastapi import APIRouter, HTTPException

from app.models import User
from app.dependencies import db_dep
from app.utils import hashed_password, verify_password
from app.schemas.auth import (
    UserRegisterIn, 
    UserRegisterOut,
    UserLoginIn
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register/", response_model=UserRegisterOut)
async def register(db: db_dep, user_in: UserRegisterIn):
    new_user = User(
        email=user_in.email,
        role=user_in.role,
        hashed_password=hashed_password(user_in.password)
        )
    
    db.add(new_user)
    db.commit()
    db.refresh(instance=new_user)

    return new_user


@router.post("/login/", response_model=UserRegisterOut)
async def login(db: db_dep, user_in: UserLoginIn):
    user = db.query(User).filter(User.email==user_in.email).first()

    if not user:
        raise HTTPException(detail="User not found.", status_code=404)
    
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(detail="Invalid credintials", status_code=403)
    
    return user