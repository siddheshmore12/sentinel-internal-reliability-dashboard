"""
HTTP/HTTPS URL health check strategy.

Health evaluation rules (single source of truth — also documented in README):
  ┌─────────────────────────────┬────────────┐
  │ Response                    │ Status     │
  ├─────────────────────────────┼────────────┤
  │ 2xx                         │ UP         │
  │ 4xx                         │ DEGRADED   │
  │ 5xx                         │ DOWN       │
  │ Timeout / connection error  │ DOWN       │
  └─────────────────────────────┴────────────┘

Latency is measured as wall-clock time from request send to first response
byte (httpx reads headers before body — this gives a realistic signal for
API availability without pulling potentially large response bodies).
"""

import time

import httpx

from app.models.enums import HealthStatus
from app.strategies.base import BaseHealthCheckStrategy, CheckResult


class URLHealthCheckStrategy(BaseHealthCheckStrategy):
    def __init__(self, timeout_seconds: float = 10.0) -> None:
        self.timeout_seconds = timeout_seconds

    async def check(self, url: str) -> CheckResult:
        start = time.monotonic()
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
            latency_ms = round((time.monotonic() - start) * 1000, 2)
            return CheckResult(
                status=self._evaluate_status_code(response.status_code),
                latency_ms=latency_ms,
                status_code=response.status_code,
            )

        except httpx.TimeoutException:
            latency_ms = round((time.monotonic() - start) * 1000, 2)
            return CheckResult(
                status=HealthStatus.DOWN,
                latency_ms=latency_ms,
                error_message="Request timed out",
            )

        except Exception as exc:
            latency_ms = round((time.monotonic() - start) * 1000, 2)
            return CheckResult(
                status=HealthStatus.DOWN,
                latency_ms=latency_ms,
                error_message=str(exc),
            )

    @staticmethod
    def _evaluate_status_code(status_code: int) -> HealthStatus:
        """Map HTTP status code to a HealthStatus enum value."""
        if 200 <= status_code < 300:
            return HealthStatus.UP
        if 400 <= status_code < 500:
            return HealthStatus.DEGRADED
        # 5xx, redirects without resolution, and edge cases → DOWN
        return HealthStatus.DOWN
