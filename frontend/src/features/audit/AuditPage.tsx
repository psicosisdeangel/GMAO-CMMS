import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { auditApi } from '../../api/audit';
import { Button } from '../../components/ui/Button';
import { Spinner } from '../../components/ui/Spinner';
import { Alert } from '../../components/ui/Alert';

const ACTION_LABELS: Record<string, string> = {
  CREATE_EQUIPMENT: 'Crear Equipo',
  UPDATE_EQUIPMENT: 'Editar Equipo',
  DELETE_EQUIPMENT: 'Eliminar Equipo',
  CREATE_WORK_ORDER: 'Crear Orden',
  CLOSE_WORK_ORDER: 'Cerrar Orden',
  START_WORK_ORDER: 'Iniciar Orden',
  DENIED_CLOSED_ORDER: 'Intento sobre Orden Cerrada',
  CREATE_USER: 'Crear Usuario',
  DEACTIVATE_USER: 'Desactivar Usuario',
  UPDATE_USER: 'Actualizar Usuario',
};

export const AuditPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const [entityFilter, setEntityFilter] = useState('');
  const [actionFilter, setActionFilter] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['audit', page, entityFilter, actionFilter],
    queryFn: () =>
      auditApi.list({
        page,
        entity: entityFilter || undefined,
        action: actionFilter || undefined,
      }),
  });

  if (isLoading) return <Spinner fullPage />;
  if (error) return <div className="page"><Alert variant="error">Error al cargar la bitácora de auditoría.</Alert></div>;

  const totalPages = data ? Math.ceil(data.count / 20) : 1;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Bitácora de Auditoría</h1>
          <p className="page-subtitle">
            {data?.count ?? 0} registros — inmutable, retención ≥ 5 años (REQ-13)
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <div className="form-group">
          <label className="form-label">Entidad</label>
          <select
            className="form-select"
            value={entityFilter}
            onChange={(e) => { setEntityFilter(e.target.value); setPage(1); }}
          >
            <option value="">Todas</option>
            <option value="Equipment">Equipo</option>
            <option value="WorkOrder">Orden de Trabajo</option>
            <option value="User">Usuario</option>
            <option value="SparePart">Repuesto</option>
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Acción</label>
          <select
            className="form-select"
            value={actionFilter}
            onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
          >
            <option value="">Todas</option>
            {Object.entries(ACTION_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
        {(entityFilter || actionFilter) && (
          <Button
            variant="ghost"
            size="sm"
            style={{ marginTop: 20 }}
            onClick={() => { setEntityFilter(''); setActionFilter(''); setPage(1); }}
          >
            Limpiar
          </Button>
        )}
      </div>

      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Fecha / Hora</th>
              <th>Acción</th>
              <th>Entidad</th>
              <th>ID Entidad</th>
              <th>Actor</th>
            </tr>
          </thead>
          <tbody>
            {data?.results.length === 0 ? (
              <tr><td colSpan={6}>
                <div className="empty-state">
                  <div className="empty-state-icon"></div>
                  <p className="empty-state-title">Sin registros de auditoría</p>
                </div>
              </td></tr>
            ) : data?.results.map((log) => (
              <tr key={log.id_log}>
                <td className="text-muted" style={{ fontSize: 12 }}>{log.id_log}</td>
                <td style={{ fontSize: 12, whiteSpace: 'nowrap' }}>
                  {new Date(log.timestamp).toLocaleString('es-CO')}
                </td>
                <td>
                  <span style={{
                    display: 'inline-block',
                    padding: '2px 8px',
                    borderRadius: 4,
                    fontSize: 11,
                    fontWeight: 600,
                    background: log.action.includes('DENIED') ? 'var(--color-danger-bg)' : 'var(--color-primary-bg)',
                    color: log.action.includes('DENIED') ? 'var(--color-danger)' : 'var(--color-primary)',
                  }}>
                    {ACTION_LABELS[log.action] ?? log.action}
                  </span>
                </td>
                <td>{log.entity}</td>
                <td><span className="font-mono" style={{ fontSize: 12 }}>{log.entity_id}</span></td>
                <td>{log.actor_username ?? <span className="text-muted">Sistema</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {totalPages > 1 && (
          <div className="pagination">
            <span className="pagination-info">
              Página {page} de {totalPages} ({data?.count} registros)
            </span>
            <div className="pagination-controls">
              <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
                Anterior
              </Button>
              <Button variant="secondary" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
                Siguiente
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
