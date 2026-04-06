"""
Abstract base for health check strategies.

Why the Strategy Pattern?
  The worker needs to probe many different service types (HTTP endpoints,
  databases, TCP ports, gRPC services, etc.).  Without the Strategy Pattern,
  a single giant if/elif block would handle all check types, making it hard
  to add new ones without touching existing logic — a violation of the
  Open/Closed Principle.

  With this pattern:
    - Each check type lives in its own class with clear, isolated logic
    - The worker calls strategy.check(url) without knowing which type it is
    - A new check type = a new file + one line in factory.py
    - Existing strategies are never modified

Adding a new strategy:
  1. Create a new file in app/strategies/
  2. Subclass BaseHealthCheckStrategy
  3. Implement async check(url) -> CheckResult
  4. Register it in factory.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.models.enums import HealthStatus


@dataclass
class CheckResult:
    """
    The result of one health probe execution.

    Always populated: status
    Optional: latency_ms (None if check errored before getting a response),
              status_code (None for non-HTTP checks or on network failure),
              error_message (populated on exception/timeout)
    """
    status: HealthStatus
    latency_ms: float | None = field(default=None)
    status_code: int | None = field(default=None)
    error_message: str | None = field(default=None)


class BaseHealthCheckStrategy(ABC):
    """All health check strategies must implement this interface."""

    @abstractmethod
    async def check(self, url: str) -> CheckResult:
        """
        Probe the given URL/address and return a CheckResult.

        Implementations must:
          - Never raise exceptions (catch and return DOWN instead)
          - Always measure latency even on failure (for trend visibility)
          - Respect the configured timeout
        """
        ...
