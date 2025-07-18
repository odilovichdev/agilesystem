import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

from app.models import User
from app.utils import create_jwt_token
from app.dependencies import db_dep, current_user_dep
from app.utils import hashed_password, verify_password
from app.schemas.auth import (
    UserRegisterIn, 
    UserRegisterOut,
    UserLoginIn,
    UserLoginOut
)

load_dotenv(Path(__name__).resolve().parent / ".env")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

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


@router.post("/login/", response_model=UserLoginOut)
async def login(db: db_dep, user_in: UserLoginIn):

    user = db.query(User).filter(User.email==user_in.email).first()

    if not user:
        raise HTTPException(detail="User not found.", status_code=404)
    
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(detail="Invalid credintials", status_code=403)
    
    access_token = create_jwt_token(
        data={
        "user_id": user.id,
        "email": user.email
    },
    expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = create_jwt_token(
        data={
        "user_id": user.id,
        "email": user.email
    },
    expires_delta=REFRESH_TOKEN_EXPIRE_MINUTES
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }


@router.get("/profile/", response_model=UserRegisterOut)
async def get_user_profile(current_user: current_user_dep):
    return current_user




