"""
HealthCheck model — stores each probe result for a service.

One row per check run. The worker inserts rows here every 60 seconds.
The frontend queries recent rows to render the latency trend chart.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import HealthStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


class HealthCheck(Base):
    __tablename__ = "health_checks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, index=True
    )
    # Wall-clock latency from when the request was sent to when the response
    # headers arrived (or the timeout fired). Stored as ms for readability.
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[HealthStatus] = mapped_column(
        SAEnum(HealthStatus, name="health_status_enum"),
        nullable=False,
        default=HealthStatus.UNKNOWN,
    )
    # Populated on timeout or connection error
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    service: Mapped["Service"] = relationship("Service", back_populates="health_checks")  # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<HealthCheck service_id={self.service_id} "
            f"status={self.status.value} latency={self.latency_ms}ms>"
        )
