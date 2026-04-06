"""
Application configuration via environment variables.

Uses pydantic-settings for type-validated, environment-driven config.
This pattern lets the same codebase run locally, in Docker, or in a
cloud environment — only environment variables change, never code.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "Sentinel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://sentinel:sentinel@localhost:5432/sentinel"
    )

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    # How long (seconds) the dashboard summary JSON lives in Redis before the
    # worker refreshes it. 30 s balances freshness vs. DB load.
    CACHE_TTL_SECONDS: int = 30

    # ── Background Worker ─────────────────────────────────────────────────────
    HEALTH_CHECK_INTERVAL_SECONDS: int = 60
    HEALTH_CHECK_TIMEOUT_SECONDS: int = 10

    # ── Observability ─────────────────────────────────────────────────────────
    METRICS_ENABLED: bool = True

    model_config = {"env_file": ".env", "case_sensitive": True}


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance — safe to use with FastAPI Depends()."""
    return Settings()
