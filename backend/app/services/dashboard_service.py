"""
Dashboard summary builder — business logic kept out of the route handler.

Building the dashboard summary requires:
  1. Fetching all registered services
  2. Querying the latest health check per service (determines card color)
  3. Counting open incidents for the summary header
  4. Aggregating status counts (up/degraded/down/unknown/maintenance)

This function is intentionally reusable:
  - Called by GET /api/v1/dashboard on a cache miss
  - Called by the background worker after each check run to pre-populate Redis
    so the next dashboard request hits the cache, not this query path.

Maintenance mode behavior:
  - Services with maintenance_mode=True show status UNKNOWN on the dashboard
    (health checks may still run, but we don't show a RED card to avoid
    triggering unnecessary on-call escalations during a known window).
  - They are counted in the `maintenance` bucket, not the `down` bucket.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import HealthStatus
from app.repositories.health_check_repo import HealthCheckRepository
from app.repositories.incident_repo import IncidentRepository
from app.repositories.service_repo import ServiceRepository
from app.schemas.dashboard import DashboardSummary, ServiceStatusCard


async def build_dashboard_summary(db: AsyncSession) -> DashboardSummary:
    """Query PostgreSQL and return a fully populated DashboardSummary."""
    service_repo = ServiceRepository(db)
    hc_repo = HealthCheckRepository(db)
    incident_repo = IncidentRepository(db)

    services = await service_repo.get_all()
    open_incidents = await incident_repo.count_open()

    cards: list[ServiceStatusCard] = []
    counts: dict[str, int] = {
        "up": 0,
        "degraded": 0,
        "down": 0,
        "unknown": 0,
        "maintenance": 0,
    }

    for svc in services:
        latest = await hc_repo.get_latest_for_service(svc.id)
        latency = latest.latency_ms if latest else None

        if svc.maintenance_mode:
            # Don't let a maintenance window inflate the DOWN count.
            display_status = HealthStatus.UNKNOWN
            counts["maintenance"] += 1
        else:
            display_status = latest.status if latest else HealthStatus.UNKNOWN
            counts[display_status.value] += 1

        cards.append(
            ServiceStatusCard(
                service_id=str(svc.id),
                name=svc.name,
                environment=svc.environment.value,
                status=display_status,
                latest_latency_ms=latency,
                maintenance_mode=svc.maintenance_mode,
            )
        )

    return DashboardSummary(
        total_services=len(services),
        up=counts["up"],
        degraded=counts["degraded"],
        down=counts["down"],
        unknown=counts["unknown"],
        maintenance=counts["maintenance"],
        open_incidents=open_incidents,
        services=cards,
    )
