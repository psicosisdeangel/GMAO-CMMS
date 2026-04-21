import client from './client';
import type { Equipment, PaginatedResponse } from '../types/api';

export const equipmentApi = {
  list: async (params?: {
    page?: number;
    search?: string;
  }): Promise<PaginatedResponse<Equipment>> => {
    const { data } = await client.get<PaginatedResponse<Equipment>>(
      '/api/equipment/',
      { params }
    );
    return data;
  },

  getById: async (id_unico: string): Promise<Equipment> => {
    const { data } = await client.get<Equipment>(`/api/equipment/${id_unico}/`);
    return data;
  },

  create: async (
    payload: Omit<Equipment, 'created_at' | 'updated_at'>
  ): Promise<Equipment> => {
    const { data } = await client.post<Equipment>('/api/equipment/', payload);
    return data;
  },

  update: async (
    id_unico: string,
    payload: Partial<Omit<Equipment, 'id_unico' | 'created_at' | 'updated_at'>>
  ): Promise<Equipment> => {
    const { data } = await client.patch<Equipment>(
      `/api/equipment/${id_unico}/`,
      payload
    );
    return data;
  },

  delete: async (id_unico: string): Promise<void> => {
    await client.delete(`/api/equipment/${id_unico}/`);
  },
};
