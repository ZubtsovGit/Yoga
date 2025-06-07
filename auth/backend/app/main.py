import asyncio
import os

from contextlib import asynccontextmanager

from bot.main import start_bot
from database import db
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from routes import router as auth_router
from utils.metrics import start_metrics_server_in_thread, track_request, time_request


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path
        
        with time_request(method, path):
            response = await call_next(request)
            
        status_code = response.status_code
        track_request(method, path, status_code)
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Установка имени сервиса для метрик
    os.environ['SERVICE_NAME'] = 'auth-backend'
    
    # Запуск сервера метрик на порту 8005
    start_metrics_server_in_thread(port=8005)
    
    db.create_db_and_tables()

    bot_task = asyncio.create_task(start_bot())
    yield
    bot_task.cancel()

    try:
        await bot_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)

# Добавление middleware для сбора метрик
app.add_middleware(PrometheusMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
