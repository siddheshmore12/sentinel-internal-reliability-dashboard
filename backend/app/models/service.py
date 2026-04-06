"""
Service model — represents a registered internal service to be monitored.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import CheckType, Environment


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    environment: Mapped[Environment] = mapped_column(
        SAEnum(Environment, name="environment_enum"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    check_type: Mapped[CheckType] = mapped_column(
        SAEnum(CheckType, name="check_type_enum"),
        nullable=False,
        default=CheckType.HTTP,
    )
    # When True: health checks still run but alerts/incidents are suppressed.
    # This reduces on-call fatigue during planned maintenance windows.
    maintenance_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, onupdate=_now
    )

    # Relationships
    health_checks: Mapped[list["HealthCheck"]] = relationship(  # noqa: F821
        "HealthCheck", back_populates="service", cascade="all, delete-orphan"
    )
    incidents: Mapped[list["Incident"]] = relationship(  # noqa: F821
        "Incident", back_populates="service", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Service name={self.name!r} env={self.environment.value}>"
