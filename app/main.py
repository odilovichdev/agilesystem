from fastapi import FastAPI

from app.routers import (
    auth_router, 
    project_router, 
    user_router, 
    task_router
)

app = FastAPI()

@app.get("/")
async def main():
    return {"message": "Hello"}

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(user_router)
app.include_router(task_router)