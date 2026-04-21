import { useAuth } from './useAuth';

export interface UsePermissionsReturn {
  canManageEquipment: boolean;
  canSchedulePreventive: boolean;
  canViewAllOrders: boolean;
  canManageUsers: boolean;
  canViewDashboard: boolean;
  canGenerateReports: boolean;
  canRegisterFault: boolean;
  canCloseOwnOrder: boolean;
}

export function usePermissions(): UsePermissionsReturn {
  const { isSupervisor, isTecnico } = useAuth();

  return {
    canManageEquipment: isSupervisor,
    canSchedulePreventive: isSupervisor,
    canViewAllOrders: isSupervisor,
    canManageUsers: isSupervisor,
    canViewDashboard: isSupervisor,
    canGenerateReports: isSupervisor,
    canRegisterFault: isSupervisor || isTecnico,
    canCloseOwnOrder: isSupervisor || isTecnico,
  };
}
