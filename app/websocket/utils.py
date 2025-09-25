# import os
# import json
# import redis.asyncio as aioredis
# from redis.exceptions import ResponseError

# from app.settings import REDIS_URL
# from app.enums import WSEventTypes, Role
# from app.websocket.manager import WSManager


# REDIS_STREAM_KEY = "ws_events"
# CONSUMER_GROUP = "ws_group"
# CONSUMER_NAME = f"worker_{os.getpid()}"


# async def get_redis():
#     return await aioredis.from_url(REDIS_URL, decode_responses=True)


# async def publish_event(event: dict):
#     redis = await get_redis()
#     await redis.xadd(REDIS_STREAM_KEY, {"data": json.dumps(event)})


# async def handle_event(ws_manager: WSManager, data: dict):
#     project_id = data["project_id"]
#     message = data["message"]
#     allowed_roles = data["allowed_roles"]

#     if "*" in allowed_roles:
#         await ws_manager.send_to_all_project_members(project_id, message)
#     else:
#         await ws_manager.send_to_roles(project_id, message, allowed_roles)


# async def dispatch_ws_event(event_type: str, project_id: int, payload: dict):
#     if event_type == WSEventTypes.task_created:
#         allowed_roles = [Role.developer, Role.tester]
#     elif event_type == WSEventTypes.task_status_change:
#         allowed_roles = [Role.manager]
#     elif event_type == WSEventTypes.task_move_ready:
#         allowed_roles = [Role.tester]
#     elif event_type == WSEventTypes.task_rejected:
#         allowed_roles = [Role.developer]
#     elif event_type == WSEventTypes.task_created_high:
#         allowed_roles = ["*"]
#     else:
#         return

#     await publish_event(
#         {
#             "project_id": project_id,
#             "allowed_roles": allowed_roles,
#             "message": payload,
#         }
#     )


# async def consume_events(ws_manager: WSManager):
#     redis = await get_redis()

#     # Create group if not exists
#     try:
#         await redis.xgroup_create(
#             REDIS_STREAM_KEY, CONSUMER_GROUP, id="0", mkstream=True
#         )
#     except ResponseError:
#         pass  # group already exists

#     while True:
#         entries = await redis.xreadgroup(
#             groupname=CONSUMER_GROUP,
#             consumername=CONSUMER_NAME,
#             streams={REDIS_STREAM_KEY: ">"},
#             count=10,
#             block=5000,  # ms
#         )

#         if entries:
#             for _, messages in entries:
#                 for msg_id, msg_data in messages:
#                     data = json.loads(msg_data["data"])
#                     await handle_event(ws_manager, data)
#                     await redis.xack(REDIS_STREAM_KEY, CONSUMER_GROUP, msg_id)
