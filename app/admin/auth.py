from datetime import timedelta, datetime, UTC

from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AuthProvider
from starlette_admin.exceptions import LoginFailed

from app.enums import Role
from app.models import User
from app.dependencies import get_db
from app.utils import verify_password
from app.settings import (
    ADMIN_REMEMBER_ME_EXPIRE_MINUTES,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
)


class StarletteAuthProvider(AuthProvider):
    async def login(
        self,
        email: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        db: Session = next(get_db())
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise LoginFailed("User not found.")

        if user and user.role != Role.admin.value:
            raise LoginFailed("User is not admin.")

        if not verify_password(password, user.hashed_password):
            raise LoginFailed("Invalid password.")

        if remember_me:
            access_token_expires = timedelta(minutes=ADMIN_REMEMBER_ME_EXPIRE_MINUTES)
        else:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        token_data = {
            "sub": user.email,
            "exp": datetime.now(UTC) + access_token_expires,
        }

        access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=True,
            httponly=True,
            samesite="lax",
        )

        return response

    async def is_authenticated(self, request: Request):
        token = request.cookies.get("access_token")

        if not token:
            return None

        try:
            payload = jwt.encode(token, SECRET_KEY, algorithm=ALGORITHM)
            email: str = payload.get("sub")

            if not email:
                return None

            db: Session = next(get_db())
            user = db.query(User).filter(User.email == email).first()

            if user is None or user.role != Role.admin.value:
                return None
            return user
        except JWTError:
            return None

    async def logout(self, request: Request, response: Response) -> Response:
        response.delete_cookie("access_token")
        return response
