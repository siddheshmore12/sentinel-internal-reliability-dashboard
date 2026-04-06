"""
Health Checks API routes.

Provides endpoints for fetching the historical probe results of a service,
used to render the latency trend charts on the frontend.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.health_check_repo import HealthCheckRepository
from app.repositories.service_repo import ServiceRepository
from app.schemas.health_check import HealthCheckResponse

router = APIRouter()


@router.get(
    "/service/{service_id}",
    response_model=list[HealthCheckResponse],
    summary="Get recent health checks for a service",
)
async def get_service_health_checks(
    service_id: UUID, 
    hours: int = Query(24, description="Hours of history to fetch"),
    limit: int = Query(200, description="Max number of records to return"),
    db: AsyncSession = Depends(get_db)
) -> list[HealthCheckResponse]:
    service_repo = ServiceRepository(db)
    if not await service_repo.get_by_id(service_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

    hc_repo = HealthCheckRepository(db)
    # The frontend needs chronological order for the React chart, but
    # the repo returns desc(). We'll reverse it here.
    checks = await hc_repo.get_recent_for_service(service_id, hours=hours, limit=limit)
    return list(reversed(checks))
