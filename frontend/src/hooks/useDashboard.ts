import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';

export const POLLING_INTERVAL = 10000; // 10 seconds

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: api.getDashboard,
    refetchInterval: POLLING_INTERVAL,
  });
}

export function useServiceDetails(id: string) {
  return useQuery({
    queryKey: ['service', id],
    queryFn: () => api.getService(id),
    enabled: !!id,
  });
}

export function useServiceHistory(id: string) {
  return useQuery({
    queryKey: ['service-history', id],
    queryFn: () => api.getServiceHealthChecks(id),
    enabled: !!id,
    refetchInterval: POLLING_INTERVAL,
  });
}

export function useMaintenanceToggle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, enabled }: { id: string; enabled: boolean }) => 
      api.updateServiceMaintenance(id, enabled),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['service', id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
