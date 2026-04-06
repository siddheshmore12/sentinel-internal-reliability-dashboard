"""
Risk assessment rule engine — automatically computes incident priority.

Design philosophy:
  The engineer reporting an incident declares *severity* (their subjective
  read of impact).  The system computes *priority* (the order in which the
  on-call team should respond) using objective rules about service criticality.

  This mirrors how mature SRE teams triage pages: a LOW severity incident on
  the Payment service still pages the on-call immediately, because the blast
  radius of a Payment outage is always HIGH regardless of first impressions.

Extending the rule engine:
  1. Subclass RiskRule
  2. Implement applies() + priority()
  3. Insert the new instance into RULES at the correct position

Rules are evaluated in order — the first match wins.
No changes to routes, repositories, or schemas are needed.
"""

from app.models.enums import IncidentPriority, IncidentSeverity
from app.models.service import Service


class RiskRule:
    """Abstract base for a single priority-evaluation rule."""

    def applies(self, service: Service, severity: IncidentSeverity) -> bool:
        raise NotImplementedError

    def priority(self) -> IncidentPriority:
        raise NotImplementedError


class PaymentServiceRule(RiskRule):
    """
    Any incident on a payment-related service is immediately HIGH priority.

    Rationale: payment services directly affect revenue.  Even a MEDIUM
    severity degradation warrants immediate escalation to minimize financial
    exposure and SLA breach risk.
    """

    def applies(self, service: Service, severity: IncidentSeverity) -> bool:
        return "payment" in service.name.lower()

    def priority(self) -> IncidentPriority:
        return IncidentPriority.HIGH


class CriticalSeverityRule(RiskRule):
    """CRITICAL severity always maps to HIGH priority regardless of service."""

    def applies(self, service: Service, severity: IncidentSeverity) -> bool:
        return severity == IncidentSeverity.CRITICAL

    def priority(self) -> IncidentPriority:
        return IncidentPriority.HIGH


class HighSeverityRule(RiskRule):
    """HIGH severity maps to MEDIUM priority (CRITICAL is already handled above)."""

    def applies(self, service: Service, severity: IncidentSeverity) -> bool:
        return severity == IncidentSeverity.HIGH

    def priority(self) -> IncidentPriority:
        return IncidentPriority.MEDIUM


# ── Rule registry ──────────────────────────────────────────────────────────────
# Ordered: first matching rule wins. Add new rules here to extend triage logic.
RULES: list[RiskRule] = [
    PaymentServiceRule(),
    CriticalSeverityRule(),
    HighSeverityRule(),
]


def compute_priority(
    service: Service, severity: IncidentSeverity
) -> IncidentPriority:
    """
    Evaluate all rules in order; return priority for the first match.
    Falls back to LOW if no rule applies.

    Called by the incident creation route — callers never set priority directly.
    """
    for rule in RULES:
        if rule.applies(service, severity):
            return rule.priority()
    return IncidentPriority.LOW
