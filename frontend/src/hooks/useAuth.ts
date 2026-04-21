import { useAuthStore } from '../store/authStore';
import type { User } from '../types/api';

export interface UseAuthReturn {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isSupervisor: boolean;
  isTecnico: boolean;
  login: (user: User, access: string, refresh: string) => void;
  logout: () => void;
}

export function useAuth(): UseAuthReturn {
  const { user, accessToken, setAuth, logout } = useAuthStore();

  return {
    user,
    accessToken,
    isAuthenticated: !!accessToken && !!user,
    isSupervisor: user?.rol === 'SUPERVISOR',
    isTecnico: user?.rol === 'TECNICO',
    login: setAuth,
    logout,
  };
}
