"""
Async PostgreSQL database connection via SQLAlchemy 2.x.

Design notes:
- We use the async engine (asyncpg driver) so FastAPI request handlers never
  block the event loop while waiting on DB I/O.
- The session factory is scoped per-request via a FastAPI dependency
  (get_db), ensuring connection pool resources are released promptly.
- Base is a shared DeclarativeBase used by all models in models/.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

# ── Engine ────────────────────────────────────────────────────────────────────
# pool_pre_ping=True: verifies connections are alive before use, preventing
# stale-connection errors after a PostgreSQL restart.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# ── Session factory ────────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Avoid implicit lazy-loads after commit
)


# ── Declarative base ───────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Shared base for all SQLAlchemy ORM models."""
    pass


# ── FastAPI dependency ─────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an async DB session for the duration of a single HTTP request.

    Usage in a route:
        async def my_route(db: AsyncSession = Depends(get_db)): ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
