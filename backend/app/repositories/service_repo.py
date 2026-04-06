"""
Service repository — all database access for the Service entity.

The repository pattern separates data-access logic from business logic and
route handlers. This means:
  - Routes never construct raw ORM queries
  - Business logic (services/) never knows which DB engine is in use
  - Repositories can be swapped or mocked cleanly in integration tests
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service import Service


class ServiceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self) -> list[Service]:
        result = await self.db.execute(select(Service).order_by(Service.name))
        return list(result.scalars().all())

    async def get_by_id(self, service_id: UUID) -> Service | None:
        result = await self.db.execute(
            select(Service).where(Service.id == service_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Service | None:
        result = await self.db.execute(
            select(Service).where(Service.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Service:
        service = Service(**kwargs)
        self.db.add(service)
        await self.db.flush()        # Get generated ID without full commit
        await self.db.refresh(service)
        return service

    async def update(self, service_id: UUID, **kwargs) -> Service | None:
        service = await self.get_by_id(service_id)
        if not service:
            return None
        for key, value in kwargs.items():
            setattr(service, key, value)
        await self.db.flush()
        await self.db.refresh(service)
        return service

    async def delete(self, service_id: UUID) -> bool:
        service = await self.get_by_id(service_id)
        if not service:
            return False
        await self.db.delete(service)
        await self.db.flush()
        return True

    async def set_maintenance_mode(self, service_id: UUID, enabled: bool) -> Service | None:
        """Toggle maintenance mode — suppresses incident creation when True."""
        return await self.update(service_id, maintenance_mode=enabled)
