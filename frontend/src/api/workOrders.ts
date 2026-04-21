import client from './client';
import type {
  WorkOrder,
  PaginatedResponse,
  WorkOrderEstado,
  WorkOrderTipo,
} from '../types/api';

export interface WorkOrderCreatePayload {
  tipo: WorkOrderTipo;
  descripcion: string;
  fecha_inicio: string;
  frecuencia: string;
  fk_equipo_id: string;
  fk_tecnico_id?: number | null;
}

export interface WorkOrderClosePayload {
  notas_cierre: string;
  spare_parts_used?: Array<{ spare_part_id: number; cantidad_usada: number }>;
}

export const workOrdersApi = {
  list: async (params?: {
    page?: number;
    estado?: WorkOrderEstado;
    tipo?: WorkOrderTipo;
    fk_equipo?: string;
  }): Promise<PaginatedResponse<WorkOrder>> => {
    const { data } = await client.get<PaginatedResponse<WorkOrder>>(
      '/api/work-orders/',
      { params }
    );
    return data;
  },

  getById: async (id: number): Promise<WorkOrder> => {
    const { data } = await client.get<WorkOrder>(`/api/work-orders/${id}/`);
    return data;
  },

  create: async (payload: WorkOrderCreatePayload): Promise<WorkOrder> => {
    const { data } = await client.post<WorkOrder>('/api/work-orders/', payload);
    return data;
  },

  update: async (
    id: number,
    payload: Partial<WorkOrderCreatePayload>
  ): Promise<WorkOrder> => {
    const { data } = await client.patch<WorkOrder>(
      `/api/work-orders/${id}/`,
      payload
    );
    return data;
  },

  start: async (id: number): Promise<WorkOrder> => {
    const { data } = await client.post<WorkOrder>(
      `/api/work-orders/${id}/start/`
    );
    return data;
  },

  close: async (
    id: number,
    payload: WorkOrderClosePayload
  ): Promise<WorkOrder> => {
    const { data } = await client.post<WorkOrder>(
      `/api/work-orders/${id}/close/`,
      payload
    );
    return data;
  },

  getEquipmentHistory: async (
    id_unico: string,
    params?: { page?: number }
  ): Promise<PaginatedResponse<WorkOrder>> => {
    const { data } = await client.get<PaginatedResponse<WorkOrder>>(
      `/api/work-orders/equipment/${id_unico}/history/`,
      { params }
    );
    return data;
  },
};
