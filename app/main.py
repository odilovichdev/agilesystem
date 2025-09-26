import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.websocket import ws_router
from app.admin.settings import admin
from app.websocket.manager import WSManager
from app.routers import (
    auth_router, 
    project_router, 
    task_router, 
    user_router,
    notif_router
)
from app.middleware import (
    SimplePrintLoggerMiddleware,
    ProcessTimeLoggerMiddleware,
    origins,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(message)s - %(asctime)s",
    handlers=[
        logging.StreamHandler(),  # Output to console
    ],
)

logger = logging.getLogger(__name__)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # before
#     ws_manager = WSManager()
#     app.state.ws_manager = ws_manager
#     task = asyncio.create_task(consume_events(app.state.ws_manager))
#     logger.info(f"Asyncio task <{task.get_name()}> is created to consume events.")
#     try:
#         yield
#     finally:
#         task.cancel()
#         logger.info(f"Asyncio task <{task.get_name()}> is cancelled.")


app = FastAPI()
app.state.ws_manager = WSManager()


@app.get("/")
async def main():
    return {"message": "Hello"}


app.include_router(auth_router)
app.include_router(project_router)
app.include_router(user_router)
app.include_router(task_router)
app.include_router(ws_router)
app.include_router(notif_router)

app.add_middleware(SimplePrintLoggerMiddleware)
app.add_middleware(ProcessTimeLoggerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# starlette admin and fastapi connections
admin.mount_to(app=app)
