from contextlib import asynccontextmanager
import os

import uvicorn

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from utils.database import db
from utils.metrics import start_metrics_server_in_thread, track_request, time_request

from application.backend.routes import router as rest_router


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
    os.environ['SERVICE_NAME'] = 'application-backend'
    
    # Запуск сервера метрик на порту 8002
    metrics_thread = start_metrics_server_in_thread(port=8002)
    
    db.create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(rest_router)

# Добавление middleware для сбора метрик
app.add_middleware(PrometheusMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
