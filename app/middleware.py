import time

from fastapi.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SimplePrintLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print("Before requests")
        response = await call_next(request)
        print("After requests")
        return response


class ProcessTimeLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start
        response.headers["Process-time"] = str(process_time)
        return response


origins = ["http://127.0.0.1:3000"]
