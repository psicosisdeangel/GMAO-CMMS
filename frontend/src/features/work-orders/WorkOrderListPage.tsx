import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { workOrdersApi } from '../../api/workOrders';
import { inventoryApi } from '../../api/inventory';
import { useAuth } from '../../hooks/useAuth';
import { Badge, getEstadoBadgeVariant, getTipoBadgeVariant } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Spinner } from '../../components/ui/Spinner';
import { Alert } from '../../components/ui/Alert';
import { WorkOrderForm } from './WorkOrderForm';
import type { WorkOrderEstado, WorkOrderTipo, SparePart } from '../../types/api';

export const WorkOrderListPage: React.FC = () => {
  const navigate = useNavigate();
  const { isSupervisor } = useAuth();
  const queryClient = useQueryClient();

  const [page, setPage] = useState(1);
  const [estadoFilter, setEstadoFilter] = useState<WorkOrderEstado | ''>('');
  const [tipoFilter, setTipoFilter] = useState<WorkOrderTipo | ''>('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Close modal state
  const [closeTarget, setCloseTarget] = useState<number | null>(null);
  const [notasCierre, setNotasCierre] = useState('');
  const [repuestosUsados, setRepuestosUsados] = useState<Array<{ spare_part_id: number; cantidad_usada: number }>>([]);
  const [closeError, setCloseError] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['work-orders', page, estadoFilter, tipoFilter],
    queryFn: () =>
      workOrdersApi.list({
        page,
        estado: estadoFilter || undefined,
        tipo: tipoFilter || undefined,
      }),
  });

  const { data: spareParts } = useQuery({
    queryKey: ['inventory', 1, ''],
    queryFn: () => inventoryApi.list({ page: 1 }),
    enabled: !!closeTarget,
  });

  const startMutation = useMutation({
    mutationFn: (id: number) => workOrdersApi.start(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['work-orders'] }),
  });

  const closeMutation = useMutation({
    mutationFn: ({ id, notas, repuestos }: { id: number; notas: string; repuestos: typeof repuestosUsados }) =>
      workOrdersApi.close(id, {
        notas_cierre: notas,
        spare_parts_used: repuestos.length ? repuestos : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-orders'] });
      setCloseTarget(null);
      setNotasCierre('');
      setRepuestosUsados([]);
      setCloseError(null);
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { error?: string } } };
      setCloseError(e.response?.data?.error || 'Error al cerrar la orden.');
    },
  });

  const handleAddRepuesto = (sp: SparePart) => {
    setRepuestosUsados((prev) => {
      if (prev.find((r) => r.spare_part_id === sp.id_repuesto)) return prev;
      return [...prev, { spare_part_id: sp.id_repuesto, cantidad_usada: 1 }];
    });
  };

  const handleRepuestoCantidad = (id: number, cantidad: number) => {
    setRepuestosUsados((prev) =>
      prev.map((r) => (r.spare_part_id === id ? { ...r, cantidad_usada: cantidad } : r))
    );
  };

  const handleRemoveRepuesto = (id: number) => {
    setRepuestosUsados((prev) => prev.filter((r) => r.spare_part_id !== id));
  };

  if (isLoading) return <Spinner fullPage />;

  if (error) {
    return (
      <div className="page">
        <Alert variant="error">Error al cargar órdenes de trabajo.</Alert>
      </div>
    );
  }

  const totalPages = data ? Math.ceil(data.count / 20) : 1;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Órdenes de Trabajo</h1>
          <p className="page-subtitle">{data?.count ?? 0} órdenes</p>
        </div>
        <div className="page-actions">
          <Button variant="primary" onClick={() => setShowCreateModal(true)}>
            + Nueva Orden
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <div className="form-group">
          <label className="form-label">Estado</label>
          <select
            className="form-select"
            value={estadoFilter}
            onChange={(e) => { setEstadoFilter(e.target.value as WorkOrderEstado | ''); setPage(1); }}
          >
            <option value="">Todos</option>
            <option value="PROGRAMADO">Programado</option>
            <option value="EN_PROCESO">En Proceso</option>
            <option value="CERRADA">Cerrada</option>
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Tipo</label>
          <select
            className="form-select"
            value={tipoFilter}
            onChange={(e) => { setTipoFilter(e.target.value as WorkOrderTipo | ''); setPage(1); }}
          >
            <option value="">Todos</option>
            <option value="PREVENTIVO">Preventivo</option>
            <option value="CORRECTIVO">Correctivo</option>
          </select>
        </div>
        {(estadoFilter || tipoFilter) && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => { setEstadoFilter(''); setTipoFilter(''); setPage(1); }}
            style={{ marginTop: 20 }}
          >
            Limpiar filtros
          </Button>
        )}
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Tipo</th>
              <th>Estado</th>
              <th>Equipo</th>
              <th>Técnico</th>
              <th>Fecha Inicio</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {data?.results.length === 0 ? (
              <tr>
                <td colSpan={7}>
                  <div className="empty-state">
                    <div className="empty-state-icon"></div>
                    <p className="empty-state-title">Sin órdenes de trabajo</p>
                    <p className="empty-state-text">Cree una nueva orden pulsando "+ Nueva Orden".</p>
                  </div>
                </td>
              </tr>
            ) : (
              data?.results.map((wo) => (
                <tr key={wo.id_orden}>
                  <td>{wo.id_orden}</td>
                  <td><Badge variant={getTipoBadgeVariant(wo.tipo)}>{wo.tipo}</Badge></td>
                  <td><Badge variant={getEstadoBadgeVariant(wo.estado)}>{wo.estado}</Badge></td>
                  <td>{wo.fk_equipo_nombre || wo.fk_equipo}</td>
                  <td>{wo.fk_tecnico_nombre ?? <span className="text-muted">Sin asignar</span>}</td>
                  <td>{new Date(wo.fecha_inicio).toLocaleDateString('es-CO')}</td>
                  <td>
                    <div className="table-actions">
                      <Button variant="ghost" size="sm" onClick={() => navigate(`/work-orders/${wo.id_orden}`)}>
                        Ver
                      </Button>
                      {wo.estado === 'PROGRAMADO' && (
                        <Button
                          variant="secondary"
                          size="sm"
                          loading={startMutation.isPending}
                          onClick={() => startMutation.mutate(wo.id_orden)}
                        >
                          Iniciar
                        </Button>
                      )}
                      {wo.estado === 'EN_PROCESO' && (
                        <Button
                          variant="success"
                          size="sm"
                          onClick={() => {
                            setCloseTarget(wo.id_orden);
                            setNotasCierre('');
                            setRepuestosUsados([]);
                            setCloseError(null);
                          }}
                        >
                          Cerrar
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {totalPages > 1 && (
          <div className="pagination">
            <span className="pagination-info">Página {page} de {totalPages}</span>
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

      {/* Create Modal */}
      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Nueva Orden de Trabajo" size="lg">
        <WorkOrderForm onSuccess={() => setShowCreateModal(false)} onCancel={() => setShowCreateModal(false)} />
      </Modal>

      {/* Close Modal */}
      <Modal
        isOpen={!!closeTarget}
        onClose={() => setCloseTarget(null)}
        title="Cerrar Orden de Trabajo"
        size="lg"
        footer={
          <>
            <Button variant="secondary" onClick={() => setCloseTarget(null)}>Cancelar</Button>
            <Button
              variant="success"
              loading={closeMutation.isPending}
              onClick={() =>
                closeTarget && closeMutation.mutate({ id: closeTarget, notas: notasCierre, repuestos: repuestosUsados })
              }
            >
              Confirmar Cierre
            </Button>
          </>
        }
      >
        {closeError && <Alert variant="error" onDismiss={() => setCloseError(null)}>{closeError}</Alert>}

        <div className="form-group">
          <label className="form-label">Notas de Cierre</label>
          <textarea
            className="form-input form-textarea"
            rows={4}
            placeholder="Describa el trabajo realizado, observaciones..."
            value={notasCierre}
            onChange={(e) => setNotasCierre(e.target.value)}
          />
        </div>

        {isSupervisor && (
          <div>
            <p className="form-label" style={{ marginBottom: 8 }}>Repuestos Utilizados (opcional)</p>
            {spareParts?.results.length ? (
              <select
                className="form-select"
                onChange={(e) => {
                  const sp = spareParts.results.find((s) => s.id_repuesto === Number(e.target.value));
                  if (sp) handleAddRepuesto(sp);
                  e.target.value = '';
                }}
              >
                <option value="">Agregar repuesto...</option>
                {spareParts.results.map((sp) => (
                  <option key={sp.id_repuesto} value={sp.id_repuesto}>
                    {sp.nombre} (Stock: {sp.cantidad_stock} {sp.unidad_medida})
                  </option>
                ))}
              </select>
            ) : null}

            {repuestosUsados.length > 0 && (
              <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
                {repuestosUsados.map((r) => {
                  const sp = spareParts?.results.find((s) => s.id_repuesto === r.spare_part_id);
                  return (
                    <div key={r.spare_part_id} className="flex items-center gap-2" style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)' }}>
                      <span style={{ flex: 1, fontSize: 13 }}>{sp?.nombre}</span>
                      <input
                        type="number"
                        min={1}
                        max={sp?.cantidad_stock}
                        value={r.cantidad_usada}
                        onChange={(e) => handleRepuestoCantidad(r.spare_part_id, Number(e.target.value))}
                        className="form-input"
                        style={{ width: 80 }}
                      />
                      <span style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>{sp?.unidad_medida}</span>
                      <Button variant="ghost" size="sm" onClick={() => handleRemoveRepuesto(r.spare_part_id)}>Quitar</Button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};
