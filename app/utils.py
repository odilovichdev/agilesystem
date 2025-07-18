import os
from pathlib import Path
from datetime import timedelta, datetime, timezone

from jose import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv(dotenv_path=Path(__name__).resolve().parent / ".env")

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(
    schemes=['argon2'],
    deprecated="auto"
)


def hashed_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password:str, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire, "token_type": "access"})

    if expires_delta != ACCESS_TOKEN_EXPIRE_MINUTES:
        to_encode.update({"exp": expire, "token_type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

