import pytest
from app.models.enums import IncidentPriority, IncidentSeverity
from app.services.risk_assessment import compute_priority
from app.models.service import Service
import uuid

@pytest.fixture
def mock_payment_service():
    return Service(id=uuid.uuid4(), name="Global Payment API")

@pytest.fixture
def mock_auth_service():
    return Service(id=uuid.uuid4(), name="Auth Service")

def test_critical_severity_always_high_priority(mock_auth_service):
    # Despite not being a payment service, CRITICAL severity demands HIGH priority
    priority = compute_priority(mock_auth_service, IncidentSeverity.CRITICAL)
    assert priority == IncidentPriority.HIGH

def test_payment_service_always_high_priority(mock_payment_service):
    # Even a LOW severity on Payment gets instantly triaged to HIGH priority
    priority = compute_priority(mock_payment_service, IncidentSeverity.LOW)
    assert priority == IncidentPriority.HIGH

def test_medium_severity_standard_service_low_priority(mock_auth_service):
    priority = compute_priority(mock_auth_service, IncidentSeverity.MEDIUM)
    assert priority == IncidentPriority.LOW
