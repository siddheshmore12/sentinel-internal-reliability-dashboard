# backend/app/models/__init__.py
# Import all models here so Alembic autogenerate can discover them.
from app.models.service import Service  # noqa: F401
from app.models.health_check import HealthCheck  # noqa: F401
from app.models.incident import Incident  # noqa: F401
