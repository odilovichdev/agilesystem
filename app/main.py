from fastapi import FastAPI

from app.routers.auth import router as auth_router


app = FastAPI()


@app.get("/")
async def main():
    return {"message": "Hello"}

app.include_router(auth_router)