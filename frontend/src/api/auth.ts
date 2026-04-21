import client from './client';
import type { LoginResponse } from '../types/api';

export interface RegisterPayload {
  username: string;
  password: string;
  nombre_completo: string;
  email?: string;
}

export const authApi = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const { data } = await client.post<LoginResponse>('/api/auth/login/', {
      username,
      password,
    });
    return data;
  },

  register: async (payload: RegisterPayload): Promise<LoginResponse> => {
    const { data } = await client.post<LoginResponse>('/api/auth/register/', payload);
    return data;
  },

  refresh: async (refresh: string): Promise<{ access: string }> => {
    const { data } = await client.post<{ access: string }>(
      '/api/auth/refresh/',
      { refresh }
    );
    return data;
  },
};
