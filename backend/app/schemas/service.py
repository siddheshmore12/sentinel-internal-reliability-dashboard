"""
Pydantic schemas for Service API input/output.

Separating schemas from ORM models is a deliberate design decision:
  - ORM models own the database structure (columns, indexes, constraints)
  - Schemas own the API contract (validation rules, field names, docs)
  - They evolve independently — API shape can change without a migration
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.models.enums import CheckType, Environment


class ServiceCreate(BaseModel):
    name: str
    environment: Environment
    url: str
    check_type: CheckType = CheckType.HTTP

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Service name must not be blank")
        return v.strip()

    @field_validator("url")
    @classmethod
    def url_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("URL must not be blank")
        return v.strip()


class ServiceUpdate(BaseModel):
    """All fields are optional — supports partial PATCH semantics."""
    name: str | None = None
    environment: Environment | None = None
    url: str | None = None
    check_type: CheckType | None = None


class ServiceResponse(BaseModel):
    id: UUID
    name: str
    environment: Environment
    url: str
    check_type: CheckType
    maintenance_mode: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MaintenanceModeUpdate(BaseModel):
    enabled: bool
