import client from './client';
import type { AuditLog, PaginatedResponse } from '../types/api';

export const auditApi = {
  list: async (params?: {
    page?: number;
    entity?: string;
    action?: string;
  }): Promise<PaginatedResponse<AuditLog>> => {
    const { data } = await client.get<PaginatedResponse<AuditLog>>(
      '/api/audit/',
      { params }
    );
    return data;
  },
};
