import { DashboardSummary, HealthCheck, Incident, Service } from '../types';

const API_BASE = '/api/v1';

async function fetcher<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorMsg = `API request failed: ${response.status} ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) errorMsg = errorData.detail;
    } catch {}
    throw new Error(errorMsg);
  }
  
  if (response.status === 204) {
    return {} as T;
  }
  
  return response.json();
}

export const api = {
  getDashboard: () => fetcher<DashboardSummary>('/dashboard'),
  
  getServices: () => fetcher<Service[]>('/services'),
  getService: (id: string) => fetcher<Service>(`/services/${id}`),
  updateServiceMaintenance: (id: string, enabled: boolean) => 
    fetcher<Service>(`/services/${id}/maintenance`, {
      method: 'POST',
      body: JSON.stringify({ enabled })
    }),
    
  getServiceHealthChecks: (id: string, hours = 24) => 
    fetcher<HealthCheck[]>(`/health-checks/service/${id}?hours=${hours}`),
    
  getIncidents: (status?: string) => 
    fetcher<Incident[]>(`/incidents${status ? `?status=${status}` : ''}`),
  reportIncident: (data: { service_id: string, severity: string, description: string }) =>
    fetcher<Incident>('/incidents/', {
      method: 'POST',
      body: JSON.stringify(data)
    })
};
