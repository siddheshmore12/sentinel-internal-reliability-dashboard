"""
Pydantic schemas for the dashboard summary endpoint.

The dashboard summary is the highest-traffic read path in Sentinel.
It is cached in Redis (TTL: 30 s) to avoid PostgreSQL being hit on
every browser poll.  These schemas define what gets serialized into
and deserialized from that Redis cache entry.
"""

from pydantic import BaseModel

from app.models.enums import HealthStatus


class ServiceStatusCard(BaseModel):
    """One entry per service in the dashboard status grid."""
    service_id: str
    name: str
    environment: str
    status: HealthStatus
    latest_latency_ms: float | None
    maintenance_mode: bool


class DashboardSummary(BaseModel):
    """
    Aggregate system health snapshot.

    Counts intentionally separate `maintenance` from status buckets —
    a service in maintenance mode doesn't inflate the `down` count,
    which would cause noisy alerting during planned windows.
    """
    total_services: int
    up: int
    degraded: int
    down: int
    unknown: int
    maintenance: int         # Services with maintenance_mode=True
    open_incidents: int
    services: list[ServiceStatusCard]
