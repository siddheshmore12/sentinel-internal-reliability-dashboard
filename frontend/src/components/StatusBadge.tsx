import { HealthStatus } from '../types';
import { cn } from '../lib/utils';
import { CheckCircle2, XCircle, AlertTriangle, Clock } from 'lucide-react';

interface StatusBadgeProps {
  status: HealthStatus;
  isMaintenance?: boolean;
}

export function StatusBadge({ status, isMaintenance }: StatusBadgeProps) {
  if (isMaintenance) {
    return (
      <span className={cn('badge', 'status-maintenance')}>
        <Clock size={12} className="mr-1" />
        Maintenance
      </span>
    );
  }

  const config = {
    up: { icon: CheckCircle2, className: 'status-up', text: 'Operational' },
    degraded: { icon: AlertTriangle, className: 'status-degraded', text: 'Degraded' },
    down: { icon: XCircle, className: 'status-down', text: 'Down' },
    unknown: { icon: Clock, className: 'status-unknown', text: 'Unknown' },
  }[status];

  const Icon = config.icon;

  return (
    <span className={cn('badge', config.className)}>
      <Icon size={12} className="mr-1 inline-block" />
      {config.text}
    </span>
  );
}
