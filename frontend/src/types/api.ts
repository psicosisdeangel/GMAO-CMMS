export type UserRole = 'TECNICO' | 'SUPERVISOR';

export interface User {
  id: number;
  username: string;
  email: string;
  nombre_completo: string;
  rol: UserRole;
  is_active: boolean;
}

export interface Equipment {
  id_unico: string;
  nombre: string;
  tipo: string;
  ubicacion: string;
  fecha_instalacion: string | null;
  estado: string;
  descripcion: string;
  created_at: string;
  updated_at: string;
}

export type WorkOrderTipo = 'PREVENTIVO' | 'CORRECTIVO';
export type WorkOrderEstado = 'PROGRAMADO' | 'EN_PROCESO' | 'CERRADA';
export type WorkOrderFrecuencia = 'UNICA' | 'MENSUAL' | 'TRIMESTRAL' | 'ANUAL';

export interface WorkOrder {
  id_orden: number;
  tipo: WorkOrderTipo;
  estado: WorkOrderEstado;
  descripcion: string;
  fecha_inicio: string;
  fecha_cierre: string | null;
  frecuencia: WorkOrderFrecuencia;
  fk_equipo: string;
  fk_equipo_nombre: string;
  fk_tecnico: number | null;
  fk_tecnico_nombre: string | null;
  notas_cierre: string;
  created_at: string;
}

export interface SparePart {
  id_repuesto: number;
  nombre: string;
  codigo: string;
  descripcion: string;
  cantidad_stock: number;
  unidad_medida: string;
}

export interface AuditLog {
  id_log: number;
  action: string;
  entity: string;
  entity_id: string;
  actor_username: string | null;
  details: Record<string, unknown>;
  timestamp: string;
}

export interface DashboardData {
  total_equipos: number;
  ordenes_por_estado: Record<string, number>;
  mttr_ultimos_30_dias_horas: number | null;
  fallas_por_equipo: Array<{ equipo_id: string; equipo_nombre: string; total_fallas: number }>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse extends AuthTokens {
  user: User;
}
