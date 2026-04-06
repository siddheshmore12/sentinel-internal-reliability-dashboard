"""
Domain enumerations for Sentinel.

All enums inherit from (str, Enum) so they:
- serialize cleanly to JSON as strings
- can be stored in PostgreSQL as native VARCHAR/ENUM columns
- are validated automatically by Pydantic schemas

Adding a new value here automatically propagates to the DB (via Alembic),
the API schema, and the frontend TypeScript types — a single source of truth.
"""

from enum import Enum


class Environment(str, Enum):
    """Deployment tier a service belongs to."""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    SANDBOX = "sandbox"


class CheckType(str, Enum):
    """
    The mechanism used to probe a service.

    The Strategy Pattern in app/strategies/ maps each CheckType to a
    concrete implementation, making it trivial to add new probe types
    (e.g., gRPC, database ping) without touching health check orchestration.
    """
    HTTP = "http"
    DATABASE = "database"
    TCP = "tcp"


class HealthStatus(str, Enum):
    """
    Result of a single health check probe.

    Evaluation rules (implemented in strategies/url_strategy.py):
      - 2xx response  → UP
      - 4xx response  → DEGRADED   (service is reachable but misbehaving)
      - 5xx / timeout → DOWN       (service is unavailable)
      - No check run  → UNKNOWN    (initial state)
    """
    UP = "up"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


class IncidentSeverity(str, Enum):
    """User-declared severity when reporting an incident."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentPriority(str, Enum):
    """
    System-computed priority, derived by the risk assessment rule engine
    in app/services/risk_assessment.py.

    Rules (in priority order):
      1. Service name contains 'payment' (case-insensitive) → HIGH
      2. Severity is CRITICAL                               → HIGH
      3. Severity is HIGH                                   → MEDIUM
      4. All other cases                                    → LOW
    """
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, Enum):
    """Lifecycle state of an incident."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"  # Auto-set when service is in maintenance mode
