"""
Pydantic schemas for Incident API input/output.

Note: IncidentCreate intentionally does NOT include `priority`.
Priority is always system-computed by the risk assessment engine —
removing it from the create schema prevents callers from bypassing
the triage rules.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import IncidentPriority, IncidentSeverity, IncidentStatus


class IncidentCreate(BaseModel):
    service_id: UUID
    severity: IncidentSeverity
    description: str


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus


class IncidentResponse(BaseModel):
    id: UUID
    service_id: UUID
    severity: IncidentSeverity
    priority: IncidentPriority      # System-computed, not user-supplied
    description: str
    status: IncidentStatus
    created_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}
