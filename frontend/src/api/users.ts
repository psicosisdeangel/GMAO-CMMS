import client from './client';
import type { User, PaginatedResponse, UserRole } from '../types/api';

export interface UserCreatePayload {
  username: string;
  email: string;
  nombre_completo: string;
  rol: UserRole;
  password: string;
}

export interface UserUpdatePayload {
  email?: string;
  nombre_completo?: string;
  rol?: UserRole;
  is_active?: boolean;
}

export const usersApi = {
  list: async (params?: {
    page?: number;
    search?: string;
  }): Promise<PaginatedResponse<User>> => {
    const { data } = await client.get<PaginatedResponse<User>>('/api/users/', {
      params,
    });
    return data;
  },

  getById: async (id: number): Promise<User> => {
    const { data } = await client.get<User>(`/api/users/${id}/`);
    return data;
  },

  create: async (payload: UserCreatePayload): Promise<User> => {
    const { data } = await client.post<User>('/api/users/', payload);
    return data;
  },

  update: async (id: number, payload: UserUpdatePayload): Promise<User> => {
    const { data } = await client.patch<User>(`/api/users/${id}/`, payload);
    return data;
  },
};
