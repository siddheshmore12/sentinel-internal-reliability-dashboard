export type Environment = 'production' | 'staging' | 'development' | 'sandbox';
export type CheckType = 'http' | 'database' | 'tcp';
export type HealthStatus = 'up' | 'degraded' | 'down' | 'unknown';
export type IncidentSeverity = 'critical' | 'high' | 'medium' | 'low';
export type IncidentPriority = 'high' | 'medium' | 'low';
export type IncidentStatus = 'open' | 'investigating' | 'resolved' | 'suppressed';

export interface Service {
  id: string;
  name: string;
  environment: Environment;
  url: string;
  check_type: CheckType;
  maintenance_mode: boolean;
  created_at: string;
  updated_at: string;
}

export interface HealthCheck {
  id: string;
  service_id: string;
  timestamp: string;
  latency_ms: number | null;
  status_code: number | null;
  status: HealthStatus;
  error_message: string | null;
}

export interface Incident {
  id: string;
  service_id: string;
  severity: IncidentSeverity;
  priority: IncidentPriority;
  description: string;
  status: IncidentStatus;
  created_at: string;
  resolved_at: string | null;
}

export interface ServiceStatusCard {
  service_id: string;
  name: string;
  environment: Environment;
  status: HealthStatus;
  latest_latency_ms: number | null;
  maintenance_mode: boolean;
}

export interface DashboardSummary {
  total_services: number;
  up: number;
  degraded: number;
  down: number;
  unknown: number;
  maintenance: number;
  open_incidents: number;
  services: ServiceStatusCard[];
}
