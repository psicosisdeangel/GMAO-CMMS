import client from './client';
import type { DashboardData } from '../types/api';

export interface MttrReport {
  month: string;
  mttr_horas: number | null;
  total_ordenes_correctivas_cerradas: number;
}

export const reportsApi = {
  getDashboard: async (): Promise<DashboardData> => {
    const { data } = await client.get<DashboardData>(
      '/api/reports/dashboard/'
    );
    return data;
  },

  getMttr: async (month: string): Promise<MttrReport> => {
    const { data } = await client.get<MttrReport>('/api/reports/mttr/', {
      params: { month },
    });
    return data;
  },
};
