"""
Sentinel FastAPI application entrypoint.

Startup/shutdown lifecycle:
  - On startup: verify DB tables exist (Alembic handles production migrations;
    create_all is a safety net for local dev without running alembic upgrade).
  - On shutdown: dispose the async connection pool gracefully so no connections
    are left dangling in the PostgreSQL server.

Routes are registered in Phase 3 (api/routes/).
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # ── Startup ───────────────────────────────────────────────────────────────
    async with engine.begin() as conn:
        # In production: run `alembic upgrade head` in CI/CD pipeline instead.
        # This create_all is a convenient local development fallback only.
        await conn.run_sync(Base.metadata.create_all)

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Internal reliability dashboard for tracking service health, "
        "incidents, and operational metrics."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from prometheus_client import make_asgi_app

# ── Health probe (used by Docker Compose healthcheck) ─────────────────────────
@app.get("/health", tags=["system"])
async def health_probe() -> dict:
    return {"status": "ok", "version": settings.APP_VERSION}


# ── Metrics endpoint (Prometheus) ─────────────────────────────────────────────
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# ── Routes registered in Phase 3 ──────────────────────────────────────────────
from app.api.routes import dashboard, health_checks, incidents, maintenance, services

app.include_router(services.router, prefix="/api/v1/services", tags=["services"])
app.include_router(maintenance.router, prefix="/api/v1/services", tags=["maintenance"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["incidents"])
app.include_router(health_checks.router, prefix="/api/v1/health-checks", tags=["health-checks"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
