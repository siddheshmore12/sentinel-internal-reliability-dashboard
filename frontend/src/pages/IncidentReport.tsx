import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '../api/client';
import { CheckCircle2, AlertCircle } from 'lucide-react';

export function IncidentReport() {
  const navigate = useNavigate();
  const [serviceId, setServiceId] = useState('');
  const [severity, setSeverity] = useState('medium');
  const [description, setDescription] = useState('');
  const [success, setSuccess] = useState(false);

  // Fetch services for the dropdown
  const { data: services } = useQuery({
    queryKey: ['services'],
    queryFn: api.getServices,
  });

  const reportMutation = useMutation({
    mutationFn: api.reportIncident,
    onSuccess: () => {
      setSuccess(true);
      setTimeout(() => navigate('/'), 2000);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!serviceId || !description.trim()) return;
    
    reportMutation.mutate({
      service_id: serviceId,
      severity,
      description
    });
  };

  if (success) {
    return (
      <div className="card max-w-lg mx-auto text-center py-12 mt-12">
        <div className="flex justify-center text-success mb-4"><CheckCircle2 size={48} /></div>
        <h2>Incident Reported</h2>
        <p className="text-muted mt-2">The system has automatically calculated priority and paged the on-call engineer.</p>
        <p className="text-sm mt-4">Redirecting to dashboard...</p>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto mt-8">
      <h1 className="mb-2">Report Incident</h1>
      <p className="text-muted mb-8">Declare a service disruption. The system will automatically compute priority based on service criticality rules.</p>
      
      <div className="card">
        <form onSubmit={handleSubmit}>
          {reportMutation.isError && (
            <div className="bg-red-900/20 border border-red-500/50 text-red-400 p-3 rounded mb-6 flex items-center gap-2">
              <AlertCircle size={18} />
              Failed to report incident. Please try again.
            </div>
          )}

          <div className="form-group">
            <label className="form-label" htmlFor="service">Affected Service</label>
            <select 
              id="service" 
              className="form-control" 
              value={serviceId}
              onChange={(e) => setServiceId(e.target.value)}
              required
            >
              <option value="" disabled>Select a service</option>
              {services?.map(s => (
                <option key={s.id} value={s.id}>{s.name} ({s.environment})</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="severity">Perceived Severity</label>
            <select 
              id="severity" 
              className="form-control"
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
            >
              <option value="critical">Critical (Complete outage)</option>
              <option value="high">High (Severe degradation)</option>
              <option value="medium">Medium (Partial disruption)</option>
              <option value="low">Low (Minor issue)</option>
            </select>
          </div>

          <div className="form-group mb-6">
            <label className="form-label" htmlFor="description">Description</label>
            <textarea 
              id="description" 
              className="form-control" 
              placeholder="Describe the symptoms and impact..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              rows={4}
            />
          </div>

          <div className="flex gap-4">
            <button 
              type="submit" 
              className="btn btn-primary ml-auto"
              disabled={reportMutation.isPending || !serviceId || !description.trim()}
            >
              {reportMutation.isPending ? 'Reporting...' : 'Submit Report'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
