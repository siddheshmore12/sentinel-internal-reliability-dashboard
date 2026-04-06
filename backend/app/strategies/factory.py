"""
Strategy factory — resolves a CheckType to a concrete strategy instance.

Centralising this mapping means the worker never imports strategy
classes directly; it only calls get_strategy().  Swapping implementations
or adding new ones requires editing only this file.
"""

from app.core.config import get_settings
from app.models.enums import CheckType
from app.strategies.base import BaseHealthCheckStrategy
from app.strategies.database_strategy import DatabaseHealthCheckStrategy
from app.strategies.url_strategy import URLHealthCheckStrategy


def get_strategy(check_type: CheckType) -> BaseHealthCheckStrategy:
    """Return the strategy instance for the given check type."""
    settings = get_settings()

    registry: dict[CheckType, BaseHealthCheckStrategy] = {
        CheckType.HTTP: URLHealthCheckStrategy(
            timeout_seconds=settings.HEALTH_CHECK_TIMEOUT_SECONDS
        ),
        CheckType.DATABASE: DatabaseHealthCheckStrategy(),
        # CheckType.TCP: TCPHealthCheckStrategy(),  ← add here when implemented
    }

    if check_type not in registry:
        raise ValueError(f"No strategy registered for check type: {check_type!r}")

    return registry[check_type]
