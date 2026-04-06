"""
Prometheus metrics registry for Sentinel.

Metrics are module-level singletons — prometheus_client handles thread safety.
They are exported via the /metrics endpoint in main.py and scraped by
Prometheus every 15 s (configured in infra/prometheus/prometheus.yml).

Metric naming follows the Prometheus convention:
  {namespace}_{subsystem}_{unit}

Grafana dashboard panels (defined in Phase 5) map to these metric names:
  Panel                    │ Metric
  ─────────────────────────┼──────────────────────────────────────────────
  Incident Rate            │ sentinel_incidents_total
  Open Incidents           │ sentinel_open_incidents
  MTTR                     │ sentinel_mttr_seconds
  Health Check Volume      │ sentinel_health_checks_total
  Check Failure Rate       │ sentinel_health_check_failures_total
  Latency Heatmap          │ sentinel_health_check_latency_ms_bucket
  Worker Iteration Time    │ sentinel_worker_run_duration_seconds_bucket
"""

from prometheus_client import Counter, Gauge, Histogram

# ── Incident metrics ──────────────────────────────────────────────────────────

INCIDENTS_TOTAL = Counter(
    "sentinel_incidents_total",
    "Total number of incidents created",
    ["severity", "priority"],   # labeled for breakdown in Grafana
)

OPEN_INCIDENTS = Gauge(
    "sentinel_open_incidents",
    "Number of currently open or investigating incidents",
)

MTTR_SECONDS = Gauge(
    "sentinel_mttr_seconds",
    "Average Mean Time To Resolve across all resolved incidents (seconds)",
)

# ── Health check metrics ───────────────────────────────────────────────────────

HEALTH_CHECKS_TOTAL = Counter(
    "sentinel_health_checks_total",
    "Total health checks performed",
    ["service_name", "status"],
)

HEALTH_CHECK_FAILURES_TOTAL = Counter(
    "sentinel_health_check_failures_total",
    "Total health checks that returned DOWN or DEGRADED",
    ["service_name"],
)

HEALTH_CHECK_LATENCY_MS = Histogram(
    "sentinel_health_check_latency_ms",
    "Health check response latency in milliseconds",
    ["service_name"],
    buckets=[50, 100, 200, 500, 1000, 2000, 5000, 10000],
)

# ── Worker metrics ─────────────────────────────────────────────────────────────

WORKER_RUN_DURATION = Histogram(
    "sentinel_worker_run_duration_seconds",
    "Wall-clock time for a single worker health check iteration across all services",
    buckets=[1, 5, 10, 30, 60, 120],
)
