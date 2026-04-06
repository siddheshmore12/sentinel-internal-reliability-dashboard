import { useParams, Link } from 'react-router-dom';
import { useServiceDetails, useServiceHistory, useMaintenanceToggle } from '../hooks/useDashboard';
import { StatusBadge } from '../components/StatusBadge';
import { LatencyChart } from '../components/LatencyChart';
import { formatDate } from '../lib/utils';
import { ArrowLeft, Server, Link as LinkIcon, PowerOff, Power } from 'lucide-react';

export function ServiceDetail() {
  const { id } = useParams<{ id: string }>();
  const { data: service, isLoading: isLoadingService } = useServiceDetails(id!);
  const { data: history, isLoading: isLoadingHistory } = useServiceHistory(id!);
  const maintenanceMutation = useMaintenanceToggle();

  if (isLoadingService) {
    return <div className="text-muted mt-8">Loading service details...</div>;
  }

  if (!service) {
    return <div className="text-danger mt-8">Service not found.</div>;
  }

  const latestStatus = history?.[history.length - 1]?.status ?? service.check_type === 'http' ? 'unknown' : 'unknown';

  const handleMaintenanceToggle = () => {
    maintenanceMutation.mutate({ id: service.id, enabled: !service.maintenance_mode });
  };

  return (
    <div>
      <Link to="/" className="btn btn-secondary inline-flex items-center gap-2 mb-6">
        <ArrowLeft size={16} /> Back to Dashboard
      </Link>

      <div className="flex-between mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1>{service.name}</h1>
            <StatusBadge status={latestStatus as any} isMaintenance={service.maintenance_mode} />
          </div>
          <div className="flex items-center gap-4 text-muted text-sm mt-2">
            <span className="flex items-center gap-1"><Server size={14} /> {service.environment}</span>
            <span className="flex items-center gap-1"><LinkIcon size={14} /> {service.url}</span>
            <span>Check via: {service.check_type}</span>
          </div>
        </div>
        
        <div>
          <button 
            className={`btn ${service.maintenance_mode ? 'btn-primary bg-amber-600 hover:bg-amber-700' : 'btn-secondary'}`}
            onClick={handleMaintenanceToggle}
            disabled={maintenanceMutation.isPending}
          >
            {service.maintenance_mode ? <Power size={16} /> : <PowerOff size={16} />}
            {service.maintenance_mode ? 'Disable Maintenance' : 'Enable Maintenance'}
          </button>
          <p className="text-xs text-muted mt-2 max-w-xs text-right">
            Disables alerts and paging for this service.
          </p>
        </div>
      </div>

      <div className="mb-8">
        <h2 className="mb-4">Latency (Last 24 Hours)</h2>
        {isLoadingHistory ? (
          <div className="chart-container flex-center text-muted">Loading chart data...</div>
        ) : (
          <LatencyChart data={history || []} />
        )}
      </div>

      <div>
        <h2 className="mb-4">Recent Checks</h2>
        <div className="card overflow-x-auto">
          <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <th className="py-2 text-muted">Time</th>
                <th className="py-2 text-muted">Status</th>
                <th className="py-2 text-muted">Latency</th>
                <th className="py-2 text-muted">Details</th>
              </tr>
            </thead>
            <tbody>
              {(history || []).slice(-10).reverse().map((check, i) => (
                <tr key={check.id} style={{ borderBottom: i < 9 ? '1px solid var(--border-color)' : 'none' }}>
                  <td className="py-3">{formatDate(check.timestamp)}</td>
                  <td className="py-3"><StatusBadge status={check.status} /></td>
                  <td className="py-3">{check.latency_ms !== null ? `${check.latency_ms} ms` : '--'}</td>
                  <td className="py-3 text-muted text-sm max-w-xs truncate">
                    {check.status_code && `HTTP ${check.status_code}`} {check.error_message}
                  </td>
                </tr>
              ))}
              {(!history || history.length === 0) && (
                <tr>
                  <td colSpan={4} className="py-4 text-center text-muted">No recent checks found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
