"""
Dashboard API route.

This is the highest traffic endpoint in the system, polled by the frontend
Dashboard view. It reads from Redis first, falling back to PostgreSQL if
the cache is cold or Redis is unavailable.
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import DASHBOARD_SUMMARY_KEY, cache_get, cache_set
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import build_dashboard_summary

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=DashboardSummary,
    summary="Get system dashboard summary",
)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
) -> DashboardSummary:
    # 1. Try to fetch from Redis first (O(1) operation)
    cached_data = await cache_get(DASHBOARD_SUMMARY_KEY)
    if cached_data:
        # We return the raw dict because FastAPI parses it into the response_model
        return cached_data

    # 2. On cache miss (or Redis failure), compute from PostgreSQL
    logger.info("Dashboard cache miss; building from PostgreSQL.")
    summary = await build_dashboard_summary(db)

    # 3. Best-effort cache populate for the next request
    # Uses model_dump(mode='json') so enums/UUIDs serialize cleanly to Redis
    await cache_set(DASHBOARD_SUMMARY_KEY, summary.model_dump(mode="json"))

    return summary
