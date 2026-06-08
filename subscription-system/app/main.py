"""Точка входа FastAPI. Запуск: uvicorn app.main:app --reload
Главная страница "/" отдаёт фронтенд-панель (frontend/index.html) — тот же origin,
поэтому проблем с CORS нет, а API доступен на тех же /auth, /customers и т.д."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app import models  # noqa: F401  — регистрирует все модели в Base.metadata
from app.api.routes import (
    auth,
    customers,
    health,
    plans,
    reports,
    subscriptions,
)
from app.config import settings
from app.database import Base, engine

# Папка с фронтендом: frontend/index.html в корне проекта
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version="1.0.0")

    # CORS — на случай, если фронтенд раздаётся с другого адреса (Неделя 5).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Base.metadata.create_all(bind=engine)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(plans.router)
    app.include_router(customers.router)
    app.include_router(subscriptions.router)
    app.include_router(reports.router)

    # Главная страница — панель управления.
    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    return app


app = create_app()
