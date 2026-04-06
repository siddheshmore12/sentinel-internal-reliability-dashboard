"""
Incidents API routes.

Incident priority is system-computed using the risk assessment engine rather 
than being accepted directly from the client.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.metrics import INCIDENTS_TOTAL, OPEN_INCIDENTS
from app.models.enums import IncidentStatus
from app.repositories.incident_repo import IncidentRepository
from app.repositories.service_repo import ServiceRepository
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentStatusUpdate
from app.services.risk_assessment import compute_priority

router = APIRouter()


@router.get("/", response_model=list[IncidentResponse], summary="List all incidents")
async def list_incidents(
    status: IncidentStatus | None = None, db: AsyncSession = Depends(get_db)
) -> list[IncidentResponse]:
    repo = IncidentRepository(db)
    return await repo.get_all(status=status)


@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report a new incident",
)
async def create_incident(
    payload: IncidentCreate, db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    service_repo = ServiceRepository(db)
    service = await service_repo.get_by_id(payload.service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

    # Compute priority based on business rules
    priority = compute_priority(service=service, severity=payload.severity)

    repo = IncidentRepository(db)
    incident = await repo.create(
        service_id=payload.service_id,
        severity=payload.severity,
        priority=priority,
        description=payload.description,
    )

    # Update Prometheus metrics
    INCIDENTS_TOTAL.labels(severity=payload.severity.value, priority=priority.value).inc()
    OPEN_INCIDENTS.inc()

    return incident


@router.get("/{incident_id}", response_model=IncidentResponse, summary="Get incident by ID")
async def get_incident(
    incident_id: UUID, db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    repo = IncidentRepository(db)
    incident = await repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")
    return incident


@router.patch(
    "/{incident_id}/status",
    response_model=IncidentResponse,
    summary="Update incident status",
)
async def update_incident_status(
    incident_id: UUID, payload: IncidentStatusUpdate, db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    repo = IncidentRepository(db)
    
    # We need the previous status to update the gauge correctly
    existing_incident = await repo.get_by_id(incident_id)
    if not existing_incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")
        
    was_open = existing_incident.status in [IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]
    is_open = payload.status in [IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]

    updated_incident = await repo.update_status(incident_id, payload.status)
    
    # Adjust open incidents gauge if crossing the open/closed boundary
    if was_open and not is_open:
        OPEN_INCIDENTS.dec()
    elif not was_open and is_open:
        OPEN_INCIDENTS.inc()
        
    return updated_incident
