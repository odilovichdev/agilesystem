from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.enums import Role
from app.models import User
from app.settings import ALGORITHM, SECRET_KEY


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]


"""#######Authentication dependencies#############"""

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login/")

oauth2_schema_dep = Annotated[str, Depends(oauth2_schema)]
oauth2_form_dep = Annotated[OAuth2PasswordRequestForm, Depends()]


async def get_current_user(db: db_dep, token: oauth2_schema_dep):
    try:
        payload = jwt.decode(
            token=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": True},
        )

        id = payload.get("user_id")

        if id is None:
            raise HTTPException(401, "Invalid access token")

        user = db.query(User).filter(User.id == id).first()

        if not user:
            raise HTTPException(404, "User Not Found.")

        if not user.is_active:
            raise HTTPException(400, "Inactive user")

        return user
    except JWTError as err:
        raise HTTPException(401, "Invalid access token") from err
    except jwt.ExpiredSignatureError as err:
        raise HTTPException(401, "Access token has expired") from err


current_user_dep = Annotated[User, Depends(get_current_user)]


async def get_project_owner(current_user: current_user_dep):
    if current_user.role != Role.owner:
        raise HTTPException(
            status_code=403,
            detail="Only project owners are allowed to perform this action.",
        )
    return current_user


async def get_project_manager(current_user: current_user_dep):
    if current_user.role != Role.manager:
        raise HTTPException(
            detail="Taskni faqat ProjectManger yarata oladi.", status_code=403
        )

    return current_user


project_owner_dep = Annotated[User, Depends(get_project_owner)]
project_manager_dep = Annotated[User, Depends(get_project_manager)]
