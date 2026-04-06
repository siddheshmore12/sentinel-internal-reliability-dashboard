import { useDashboard } from '../hooks/useDashboard';
import { ServiceCard } from '../components/ServiceCard';
import { ShieldCheck, AlertTriangle, AlertOctagon } from 'lucide-react';

export function Dashboard() {
  const { data: summary, isLoading, error } = useDashboard();

  if (isLoading) {
    return <div className="flex-center h-full text-muted mt-8">Loading dashboard metrics...</div>;
  }

  if (error || !summary) {
    return (
      <div className="card border-danger mt-8">
        <h2 className="text-danger flex items-center gap-2">
          <AlertOctagon /> Error loading dashboard
        </h2>
        <p className="mt-2 text-muted">Unable to connect to the internal telemetry API.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex-between mb-6">
        <div>
          <h1>System Status</h1>
          <p className="text-muted">Real-time health overview of all internal services.</p>
        </div>
        
        {/* Quick Stats Header */}
        <div className="flex gap-4">
          <div className="card py-2 px-4 flex items-center gap-3">
            <ShieldCheck className="text-success" />
            <div>
              <div className="stat-label">Healthy</div>
              <div className="stat-value">{summary.up} / {summary.total_services}</div>
            </div>
          </div>
          {summary.open_incidents > 0 && (
            <div className="card py-2 px-4 flex items-center gap-3 border-danger">
              <AlertTriangle className="text-danger" />
              <div>
                <div className="stat-label">Active Incidents</div>
                <div className="stat-value text-danger">{summary.open_incidents}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      <h2>Services</h2>
      <div className="status-grid">
        {summary.services.map(service => (
          <ServiceCard key={service.service_id} service={service} />
        ))}
      </div>
    </div>
  );
}
