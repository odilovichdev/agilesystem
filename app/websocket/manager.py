import asyncio
from collections import defaultdict

from fastapi import WebSocket

from app.enums import WSEventTypes, Role


class WSManager:
    """
    - Local connections = {user_id: Websocket}
    - Project members = {project_id: {user_id: role}}
    - Lock = asyncio.Lock()
    """
    def __init__(self):
        self.local_connections: dict[int, WebSocket] ={}
        self.project_members: dict[int, dict[int, str]] = defaultdict(dict)
        self.lock = asyncio.Lock()

    async def connect(
            self, websocket: WebSocket, user_id: int, role: str, projects: list[int]
    ):
        await websocket.accept()

        async with self.lock:
            self.local_connections[user_id] = websocket
            for project_id in projects:
                self.project_members[project_id][user_id] = role
    

    async def disconnect(
            self, user_id: int
    ):
        async with self.lock:
            self.local_connections.pop(user_id)
            for project in self.project_members.values():
                project.pop(user_id, None)
    

    async def send_to_roles(
            self, project_id: int, message: dict, allowed_roles: list[str]
    ):
        members = self.project_members.get(project_id)
        for user_id, role in members.items():
            if user_id in self.local_connections and role in allowed_roles:
                await self.local_connections[user_id].send_json(message)
    

    async def send_to_all_project_members(
            self, project_id: int, message: dict
    ):
        members = self.project_members.get(project_id)
        for user_id in members.keys():
            if user_id in self.local_connections.keys():
                await self.local_connections[user_id].send_json(message)


async def dispatch_ws_event(
        ws_manager: WSManager,
        event_type: str,
        project_id: int,
        payload: dict
):
    
    if event_type == WSEventTypes.task_created:
        await ws_manager.send_to_roles(
            project_id, payload, {Role.developer, Role.tester}
            )
    elif event_type == WSEventTypes.task_status_change:
        await ws_manager.send_to_roles(project_id, payload, {Role.manager, Role.developer})
    elif event_type == WSEventTypes.task_move_ready:
        await ws_manager.send_to_roles(project_id, payload, {Role.tester})
    elif event_type == WSEventTypes.task_rejected:
        await ws_manager.send_to_roles(project_id, payload, {Role.developer})
    elif event_type == WSEventTypes.task_created_high:
        await ws_manager.send_to_all_project_members(project_id, payload)
    elif event_type == WSEventTypes.task_all:
        await ws_manager.send_to_all_project_members(project_id, payload)