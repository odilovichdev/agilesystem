
from fastapi import APIRouter, HTTPException
from fastapi.background import BackgroundTasks

from app.enums import Role
from app.models import User
from app.celery import send_email
from app.utils import get_object_or_404
from app.task import write_notification
from app.dependencies import db_dep, oauth2_form_dep
from app.schemas.auth import TokenResponse, UserRegisterRequest
from app.settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    FRONTEND_URL,
)
from app.utils import (
    create_jwt_token,
    hashed_password,
    verify_password,
    generate_activation_token,
    decode_user_from_jwt,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register/")
async def register(db: db_dep, request_data: UserRegisterRequest):
    is_user_exists = db.query(User).filter(User.email == request_data.email).first()

    if is_user_exists:
        raise HTTPException(400, "User already exists.")

    is_first_user = db.query(User).count() == 0

    if is_first_user:
        user = User(
            email=request_data.email,
            hashed_password=hashed_password(request_data.password),
            role=Role.admin,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"detal": f"Admin user created with email: {user.email}"}
    user = User(
        email=request_data.email,
        hashed_password=hashed_password(request_data.password),
        role=request_data.role,
        is_active=False,
        is_deleted=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_activation_token(user_id=user.id)

    send_email.delay(
        to_email=user.email,
        subject="Confirm your register to Agile",
        body=f"You can click the link to confirm your email: {FRONTEND_URL}/auth/confirm/{token}/",
    )

    return {
        "detail": f"Confirmation email sent to {user.email}. Please confirm to finalize your registration.",
    }


@router.post("/login/")
async def login(form_data: oauth2_form_dep, db: db_dep):

    user = get_object_or_404(db, User, email=form_data.username)

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(400, "Incorrect password")

    access_token = create_jwt_token(
        {"user_id": user.id, "role": user.role}, expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    refresh_token = create_jwt_token(
        {"user_id": user.id, "role": user.role}, expires_delta=REFRESH_TOKEN_EXPIRE_MINUTES
    )

    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token, token_type="Bearer"
    )


@router.get("/confirm/{token}/")
async def confirm_email(db: db_dep, token: str):
    
    user_id = decode_user_from_jwt(token=token).get("user_id")
    user = get_object_or_404(db, User, id=user_id)

    user.is_active = True
    db.commit()
    db.refresh(user)

    return {"detail": "Email confirmed."}


@router.post("/send-notification/{email}")
async def send_notification(email: str, background_task: BackgroundTasks):
    background_task.add_task(write_notification, email, message="Some notification")
    return {"message": "Notification send in the background."}
