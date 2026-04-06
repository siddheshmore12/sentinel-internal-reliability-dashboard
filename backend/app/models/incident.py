"""
Incident model — tracks service disruptions reported by engineers.

Incidents are the core reliability primitive in Sentinel.  The risk assessment
service (app/services/risk_assessment.py) automatically computes `priority`
from the submitted severity and service metadata, simulating an internal
triage workflow and reducing cognitive load during an on-call event.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import IncidentPriority, IncidentSeverity, IncidentStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        SAEnum(IncidentSeverity, name="incident_severity_enum"), nullable=False
    )
    # priority is system-computed; the reporter only sets severity.
    priority: Mapped[IncidentPriority] = mapped_column(
        SAEnum(IncidentPriority, name="incident_priority_enum"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[IncidentStatus] = mapped_column(
        SAEnum(IncidentStatus, name="incident_status_enum"),
        nullable=False,
        default=IncidentStatus.OPEN,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    # Set when status transitions to RESOLVED.  Used to compute MTTR.
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    service: Mapped["Service"] = relationship("Service", back_populates="incidents")  # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<Incident service_id={self.service_id} "
            f"severity={self.severity.value} status={self.status.value}>"
        )
