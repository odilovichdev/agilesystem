from fastapi import APIRouter


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/unread")
async def get_unread_notification():
    ...


@router.patch("/{id}/read")
async def edit_notification():
    ...