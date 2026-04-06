"""Pydantic schemas for HealthCheck API responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import HealthStatus


class HealthCheckResponse(BaseModel):
    id: UUID
    service_id: UUID
    timestamp: datetime
    latency_ms: float | None
    status_code: int | None
    status: HealthStatus
    error_message: str | None

    model_config = {"from_attributes": True}
