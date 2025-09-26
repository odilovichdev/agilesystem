from sqlalchemy import false
from fastapi import APIRouter

from app.models import Notification
from app.utils import get_object_or_404
from app.schemas import NotificationListReponse
from app.dependencies import db_dep, current_user_dep


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/unread", response_model=list[NotificationListReponse])
async def get_unread_notification(db: db_dep, current_user: current_user_dep):
    notifications = db.query(Notification).filter(
        Notification.recipient_id==current_user.id,
        Notification.is_read==false()
    ).all()

    return notifications


@router.patch("/{notif_id:int}/read")
async def edit_notification(notif_id: int, db: db_dep, current_user: current_user_dep):
    notif = get_object_or_404(db, Notification, id=notif_id)

    notif.is_read = True
    db.commit()

    return {"detail": "Notification is read successfully."}
