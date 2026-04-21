import client from './client';
import type { SparePart, PaginatedResponse } from '../types/api';

export interface SparePartCreatePayload {
  nombre: string;
  codigo: string;
  descripcion: string;
  cantidad_stock: number;
  unidad_medida: string;
}

export const inventoryApi = {
  list: async (params?: {
    page?: number;
    search?: string;
  }): Promise<PaginatedResponse<SparePart>> => {
    const { data } = await client.get<PaginatedResponse<SparePart>>(
      '/api/inventory/',
      { params }
    );
    return data;
  },

  getById: async (id: number): Promise<SparePart> => {
    const { data } = await client.get<SparePart>(`/api/inventory/${id}/`);
    return data;
  },

  create: async (payload: SparePartCreatePayload): Promise<SparePart> => {
    const { data } = await client.post<SparePart>('/api/inventory/', payload);
    return data;
  },

  update: async (
    id: number,
    payload: Partial<SparePartCreatePayload>
  ): Promise<SparePart> => {
    const { data } = await client.patch<SparePart>(
      `/api/inventory/${id}/`,
      payload
    );
    return data;
  },
};
