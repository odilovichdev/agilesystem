from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.settings import admin
from app.routers import auth_router, project_router, task_router, user_router
from app.middleware import (
    SimplePrintLoggerMiddleware,
    ProcessTimeLoggerMiddleware,
    origins,
)

app = FastAPI(title="Agile", description="Agile system", version="0.1.0")


@app.get("/")
async def main():
    return {"message": "Hello"}


app.include_router(auth_router)
app.include_router(project_router)
app.include_router(user_router)
app.include_router(task_router)

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
