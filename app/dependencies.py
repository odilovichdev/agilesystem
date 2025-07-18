import os
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from jose import jwt
from sqlalchemy.orm import Session
from app.database import SessionLocal
from fastapi import Depends, Request, HTTPException

from app.models import User


load_dotenv(dotenv_path=Path(__name__).resolve().parent / ".env")

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 180
REFRESH_TOKEN_EXPIRE_MINUTES = 465200


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]

def get_current_user(db: db_dep, request: Request):
    auth_headers = request.headers.get("Authorization")
    is_bearer = auth_headers.startswith("Bearer") if auth_headers else False
    token = auth_headers.split(" ")[1] if auth_headers else ""

    if not auth_headers and is_bearer:
        raise HTTPException(
            detail="You are not authenticated.",
            status_code=401
        )
    
    try:
        decoded_jwt = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=ALGORITHM
        )
        print(decoded_jwt.get("token_type"), "+++++")
        if decoded_jwt.get("token_type")!="access":
            raise HTTPException(
                detail="Invalid token type=access",
                status_code=401
            )
        user_id = decoded_jwt.get("user_id")
        user = db.query(User).filter(User.id==user_id).first()
    except :
        raise HTTPException(
            detail="Invalid token.",
            status_code=401
        )

    return user


current_user_dep = Annotated[User, Depends(get_current_user)]
