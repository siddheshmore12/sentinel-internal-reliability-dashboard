"""
HealthCheck repository — reads and writes probe results.

Queries here are intentionally narrow:
  - get_recent_for_service powers the latency trend chart (24 h window)
  - count_* methods feed the Prometheus metrics endpoint
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import HealthStatus
from app.models.health_check import HealthCheck


class HealthCheckRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_recent_for_service(
        self,
        service_id: UUID,
        hours: int = 24,
        limit: int = 200,
    ) -> list[HealthCheck]:
        """Return up to `limit` checks within the last `hours` for one service."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        result = await self.db.execute(
            select(HealthCheck)
            .where(
                HealthCheck.service_id == service_id,
                HealthCheck.timestamp >= since,
            )
            .order_by(HealthCheck.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_latest_for_service(self, service_id: UUID) -> HealthCheck | None:
        """Most recent probe result — used to build the dashboard status card."""
        result = await self.db.execute(
            select(HealthCheck)
            .where(HealthCheck.service_id == service_id)
            .order_by(HealthCheck.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> HealthCheck:
        check = HealthCheck(**kwargs)
        self.db.add(check)
        await self.db.flush()
        await self.db.refresh(check)
        return check

    async def count_failures_since(self, since: datetime) -> int:
        """Count DOWN or DEGRADED results — used by the Prometheus failure gauge."""
        result = await self.db.execute(
            select(func.count(HealthCheck.id)).where(
                HealthCheck.timestamp >= since,
                HealthCheck.status.in_([HealthStatus.DOWN, HealthStatus.DEGRADED]),
            )
        )
        return result.scalar_one()

    async def count_total_since(self, since: datetime) -> int:
        """Total checks run since a given time — denominator for failure rate."""
        result = await self.db.execute(
            select(func.count(HealthCheck.id)).where(HealthCheck.timestamp >= since)
        )
        return result.scalar_one()
