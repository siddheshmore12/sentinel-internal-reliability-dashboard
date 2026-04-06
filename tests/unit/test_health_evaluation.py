import pytest
from app.models.enums import HealthStatus
from app.strategies.url_strategy import URLHealthCheckStrategy

def test_http_2xx_is_up():
    assert URLHealthCheckStrategy._evaluate_status_code(200) == HealthStatus.UP
    assert URLHealthCheckStrategy._evaluate_status_code(201) == HealthStatus.UP
    assert URLHealthCheckStrategy._evaluate_status_code(299) == HealthStatus.UP

def test_http_4xx_is_degraded():
    # 404s, 401s mean the service is up but rejecting the query / misconfigured
    assert URLHealthCheckStrategy._evaluate_status_code(400) == HealthStatus.DEGRADED
    assert URLHealthCheckStrategy._evaluate_status_code(403) == HealthStatus.DEGRADED
    assert URLHealthCheckStrategy._evaluate_status_code(404) == HealthStatus.DEGRADED

def test_http_5xx_is_down():
    # 5xx represents genuine server failures
    assert URLHealthCheckStrategy._evaluate_status_code(500) == HealthStatus.DOWN
    assert URLHealthCheckStrategy._evaluate_status_code(502) == HealthStatus.DOWN
    assert URLHealthCheckStrategy._evaluate_status_code(503) == HealthStatus.DOWN
    assert URLHealthCheckStrategy._evaluate_status_code(504) == HealthStatus.DOWN
