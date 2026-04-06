"""
Incident repository — data access for incident lifecycle management.

Notable design: `resolve()` stamps `resolved_at` automatically so MTTR
can be computed by `compute_avg_resolution_seconds()` without requiring
callers to know the timestamp logic.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import IncidentStatus
from app.models.incident import Incident


class IncidentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self, status: IncidentStatus | None = None) -> list[Incident]:
        query = select(Incident).order_by(Incident.created_at.desc())
        if status:
            query = query.where(Incident.status == status)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, incident_id: UUID) -> Incident | None:
        result = await self.db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        return result.scalar_one_or_none()

    async def get_for_service(self, service_id: UUID) -> list[Incident]:
        result = await self.db.execute(
            select(Incident)
            .where(Incident.service_id == service_id)
            .order_by(Incident.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_open(self) -> int:
        result = await self.db.execute(
            select(func.count(Incident.id)).where(
                Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING])
            )
        )
        return result.scalar_one()

    async def create(self, **kwargs) -> Incident:
        incident = Incident(**kwargs)
        self.db.add(incident)
        await self.db.flush()
        await self.db.refresh(incident)
        return incident

    async def update_status(
        self, incident_id: UUID, status: IncidentStatus
    ) -> Incident | None:
        incident = await self.get_by_id(incident_id)
        if not incident:
            return None
        incident.status = status
        # Stamp resolved_at the first time this incident is resolved
        if status == IncidentStatus.RESOLVED and incident.resolved_at is None:
            incident.resolved_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(incident)
        return incident

    async def compute_avg_resolution_seconds(self) -> float | None:
        """
        Average MTTR (Mean Time To Resolve) across all resolved incidents.

        Returns None if there are no resolved incidents yet.
        MTTR is a key reliability SLO signal — tracked in Grafana.
        """
        result = await self.db.execute(
            select(
                func.avg(
                    func.extract("epoch", Incident.resolved_at)
                    - func.extract("epoch", Incident.created_at)
                )
            ).where(Incident.resolved_at.isnot(None))
        )
        return result.scalar_one()
