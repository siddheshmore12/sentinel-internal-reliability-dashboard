"""
Services CRUD routes.

Route handlers are intentionally thin — they validate input, delegate to
the repository, and return the result.  No raw SQL, no business logic here.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.service_repo import ServiceRepository
from app.schemas.service import ServiceCreate, ServiceResponse, ServiceUpdate

router = APIRouter()


@router.get("/", response_model=list[ServiceResponse], summary="List all services")
async def list_services(db: AsyncSession = Depends(get_db)) -> list[ServiceResponse]:
    repo = ServiceRepository(db)
    return await repo.get_all()


@router.post(
    "/",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new service",
)
async def create_service(
    payload: ServiceCreate, db: AsyncSession = Depends(get_db)
) -> ServiceResponse:
    repo = ServiceRepository(db)
    if await repo.get_by_name(payload.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Service '{payload.name}' already exists.",
        )
    return await repo.create(**payload.model_dump())


@router.get("/{service_id}", response_model=ServiceResponse, summary="Get a service by ID")
async def get_service(
    service_id: UUID, db: AsyncSession = Depends(get_db)
) -> ServiceResponse:
    repo = ServiceRepository(db)
    service = await repo.get_by_id(service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")
    return service


@router.patch("/{service_id}", response_model=ServiceResponse, summary="Update service fields")
async def update_service(
    service_id: UUID,
    payload: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
) -> ServiceResponse:
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No updatable fields provided.",
        )
    repo = ServiceRepository(db)
    service = await repo.update(service_id, **updates)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")
    return service


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a service and all its history",
)
async def delete_service(
    service_id: UUID, db: AsyncSession = Depends(get_db)
) -> None:
    repo = ServiceRepository(db)
    deleted = await repo.delete(service_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")
