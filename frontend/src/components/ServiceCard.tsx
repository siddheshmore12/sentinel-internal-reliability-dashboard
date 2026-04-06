import { Link } from 'react-router-dom';
import { ServiceStatusCard } from '../types';
import { StatusBadge } from './StatusBadge';
import { formatLatency } from '../lib/utils';
import { Activity } from 'lucide-react';

interface ServiceCardProps {
  service: ServiceStatusCard;
}

export function ServiceCard({ service }: ServiceCardProps) {
  return (
    <Link to={`/service/${service.service_id}`} className="card" style={{ display: 'block' }}>
      <div className="service-card-header">
        <div>
          <h3 className="service-card-title">{service.name}</h3>
          <span className="service-card-env">{service.environment}</span>
        </div>
        <StatusBadge status={service.status} isMaintenance={service.maintenance_mode} />
      </div>
      
      <div className="service-card-stats">
        <div>
          <div className="stat-label">Latency</div>
          <div className="stat-value">{formatLatency(service.latest_latency_ms)}</div>
        </div>
        <div className="text-muted">
          <Activity size={18} />
        </div>
      </div>
    </Link>
  );
}
