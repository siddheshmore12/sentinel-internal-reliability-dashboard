"""
Database connectivity health check strategy.

STATUS: Placeholder — not yet implemented.

This class exists to demonstrate that the Strategy Pattern makes adding
new probe mechanisms a purely additive change.  Implementing database
health checks requires only filling in this class and registering it
in factory.py.  No changes to the worker, the runner, or any route
handler are needed.

Planned implementation (Phase 2 roadmap item):
  - Parse a SQLAlchemy connection URL from the `url` parameter
  - Attempt to open an async connection and run `SELECT 1`
  - Return UP if the query succeeds within timeout, DOWN otherwise
  - Handle connection pool exhaustion as DEGRADED

See GitHub issue #12 for the full implementation plan.
"""

from app.models.enums import HealthStatus
from app.strategies.base import BaseHealthCheckStrategy, CheckResult


class DatabaseHealthCheckStrategy(BaseHealthCheckStrategy):
    async def check(self, url: str) -> CheckResult:
        # TODO: implement database connectivity probe
        # Returning UNKNOWN until this is implemented so it doesn't
        # pollute the dashboard with false DOWN signals.
        return CheckResult(
            status=HealthStatus.UNKNOWN,
            error_message="DatabaseHealthCheckStrategy not yet implemented",
        )
