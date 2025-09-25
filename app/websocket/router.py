from sqlalchemy import select
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.dependencies import get_db
from app.websocket.manager import WSManager
from app.models import User, Project, ProjectMember
from app.websocket.dependencies import ws_current_user_dep


router = APIRouter(
    prefix="/ws",
    tags=['websockets']
)


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, user_data: ws_current_user_dep):
    user_id = user_data.get("user_id")
    role = user_data.get("role")

    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        projects = (
            db.execute(
                select(Project.id)
                .select_from(Project)
                .join(Project.members)
                .where(ProjectMember.user_id==user.id)
            )
            .scalars()
            .all()
        )
    finally:
        db.close()
    
    ws_manager: WSManager = websocket.app.state.ws_manager
    await ws_manager.connect(
        websocket=websocket, 
        user_id=user_id, 
        role=role, 
        projects=projects
        )
    

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "user_id": user_id,
                "role": role,
                "projects": projects
            }
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(user_id)