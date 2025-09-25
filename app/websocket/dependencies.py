import logging
from typing import Annotated, Any

from jose import jwt, JWTError
from fastapi import WebSocket, WebSocketException, status, Depends

from app.settings import (
    SECRET_KEY,
    ALGORITHM
)

logger = logging.getLogger(__name__)


async def get_current_user_ws(websocket: WebSocket) -> dict[str, Any]:
    token = websocket.query_params.get("token")

    if not token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, 
            reason="Missing token!")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload.get("user_id")
        role = payload.get("role")
        return {"user_id": user_id, "role": role}
    except (JWTError, ValueError) as e:
        logger.warning(f"Jwt error: {e}")
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token!"
        ) from e


ws_current_user_dep = Annotated[dict[str, Any], Depends(get_current_user_ws)]


