from datetime import datetime, timedelta, timezone

from jose import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hashed_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(data: dict, expires_delta: timedelta | None = None):
    """
    Creates a new JWT token for logging-in user
    """

    to_encode = data.copy()

    delta = (
        timedelta(minutes=expires_delta)
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    expire_time = datetime.now(timezone.utc) + delta
    to_encode.update({"exp": expire_time})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def generate_activation_token(user_id: int):
    return jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm=ALGORITHM)


def decode_user_from_jwt(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)


def get_object_or_404(db, model, **filters):
    obj = db.query(model).filter_by(**filters).first()
    if not obj:
        raise HTTPException(404, f"{model.__name__}")
    return obj