"""
Maintenance mode routes.

Maintenance mode allows temporarily suppressing incidents and alerts for a
service during planned downtime. The dashboard handles this gracefully by
classifying the service as 'maintenance' rather than 'down', avoiding panic.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import DASHBOARD_SUMMARY_KEY, cache_delete
from app.repositories.service_repo import ServiceRepository
from app.schemas.service import MaintenanceModeUpdate, ServiceResponse

router = APIRouter()


@router.post(
    "/{service_id}/maintenance",
    response_model=ServiceResponse,
    summary="Toggle maintenance mode for a service",
)
async def toggle_maintenance_mode(
    service_id: UUID,
    payload: MaintenanceModeUpdate,
    db: AsyncSession = Depends(get_db),
) -> ServiceResponse:
    repo = ServiceRepository(db)
    service = await repo.set_maintenance_mode(service_id, payload.enabled)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

    # Invalidate dashboard cache so the UI updates immediately
    await cache_delete(DASHBOARD_SUMMARY_KEY)

    return service
