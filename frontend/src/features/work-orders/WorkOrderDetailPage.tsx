import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { workOrdersApi } from '../../api/workOrders';
import { inventoryApi } from '../../api/inventory';
import { useAuth } from '../../hooks/useAuth';
import { Badge, getEstadoBadgeVariant, getTipoBadgeVariant } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Spinner } from '../../components/ui/Spinner';
import { Alert } from '../../components/ui/Alert';
import type { SparePart } from '../../types/api';

export const WorkOrderDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { } = useAuth();

  const [showCloseModal, setShowCloseModal] = useState(false);
  const [notasCierre, setNotasCierre] = useState('');
  const [repuestosUsados, setRepuestosUsados] = useState<Array<{ spare_part_id: number; cantidad_usada: number }>>([]);
  const [closeError, setCloseError] = useState<string | null>(null);

  const { data: wo, isLoading, error, refetch } = useQuery({
    queryKey: ['work-order', id],
    queryFn: () => workOrdersApi.getById(Number(id)),
    enabled: !!id,
  });

  const { data: spareParts } = useQuery({
    queryKey: ['inventory', 1, ''],
    queryFn: () => inventoryApi.list({ page: 1 }),
    enabled: showCloseModal,
  });

  const startMutation = useMutation({
    mutationFn: () => workOrdersApi.start(Number(id)),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['work-order', id] }); refetch(); },
  });

  const closeMutation = useMutation({
    mutationFn: () =>
      workOrdersApi.close(Number(id), {
        notas_cierre: notasCierre,
        spare_parts_used: repuestosUsados.length ? repuestosUsados : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-order', id] });
      queryClient.invalidateQueries({ queryKey: ['work-orders'] });
      setShowCloseModal(false);
      setNotasCierre('');
      setRepuestosUsados([]);
      setCloseError(null);
      refetch();
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

  if (isLoading) return <Spinner fullPage />;

  if (error || !wo) {
    return (
      <div className="page">
        <Button variant="ghost" size="sm" onClick={() => navigate('/work-orders')} style={{ marginBottom: 16 }}>
          Volver
        </Button>
        <Alert variant="error">Orden de trabajo no encontrada.</Alert>
      </div>
    );
  }

  const isClosed = wo.estado === 'CERRADA';

  return (
    <div className="page">
      <div className="page-header">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => navigate('/work-orders')}>Volver</Button>
          <div>
            <h1 className="page-title">Orden #{wo.id_orden}</h1>
            <div className="flex items-center gap-2" style={{ marginTop: 4 }}>
              <Badge variant={getTipoBadgeVariant(wo.tipo)}>{wo.tipo}</Badge>
              <Badge variant={getEstadoBadgeVariant(wo.estado)}>{wo.estado}</Badge>
            </div>
          </div>
        </div>
        <div className="page-actions">
          {wo.estado === 'PROGRAMADO' && (
            <Button variant="secondary" loading={startMutation.isPending} onClick={() => startMutation.mutate()}>
              Iniciar Orden
            </Button>
          )}
          {wo.estado === 'EN_PROCESO' && (
            <Button variant="success" onClick={() => setShowCloseModal(true)}>
              Cerrar Orden
            </Button>
          )}
        </div>
      </div>

      {isClosed && (
        <Alert variant="info" style={{ marginBottom: 16 }}>
          Esta orden está cerrada y es inmutable (REQ-05).
        </Alert>
      )}

      {/* Main info */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">Información General</h2>
        </div>
        <div className="card-body">
          <div className="detail-grid">
            <div className="detail-field">
              <div className="detail-label">Equipo</div>
              <div className="detail-value">
                <a href={`/equipment/${wo.fk_equipo}`}>{wo.fk_equipo_nombre || wo.fk_equipo}</a>
              </div>
            </div>
            <div className="detail-field">
              <div className="detail-label">Técnico Asignado</div>
              <div className="detail-value">{wo.fk_tecnico_nombre ?? '—'}</div>
            </div>
            <div className="detail-field">
              <div className="detail-label">Fecha Inicio</div>
              <div className="detail-value">{new Date(wo.fecha_inicio).toLocaleString('es-CO')}</div>
            </div>
            <div className="detail-field">
              <div className="detail-label">Fecha Cierre</div>
              <div className="detail-value">
                {wo.fecha_cierre ? new Date(wo.fecha_cierre).toLocaleString('es-CO') : '—'}
              </div>
            </div>
            {wo.tipo === 'PREVENTIVO' && (
              <div className="detail-field">
                <div className="detail-label">Frecuencia</div>
                <div className="detail-value">{wo.frecuencia}</div>
              </div>
            )}
            <div className="detail-field">
              <div className="detail-label">Creado</div>
              <div className="detail-value">{new Date(wo.created_at).toLocaleDateString('es-CO')}</div>
            </div>
          </div>

          <div className="detail-field" style={{ marginTop: 16 }}>
            <div className="detail-label">Descripción</div>
            <div className="detail-value" style={{ whiteSpace: 'pre-wrap' }}>{wo.descripcion}</div>
          </div>

          {isClosed && wo.notas_cierre && (
            <div className="detail-field" style={{ marginTop: 16 }}>
              <div className="detail-label">Notas de Cierre</div>
              <div className="detail-value" style={{ whiteSpace: 'pre-wrap' }}>{wo.notas_cierre}</div>
            </div>
          )}
        </div>
      </div>

      {/* Close Modal */}
      <Modal
        isOpen={showCloseModal}
        onClose={() => setShowCloseModal(false)}
        title={`Cerrar Orden #${wo.id_orden}`}
        size="lg"
        footer={
          <>
            <Button variant="secondary" onClick={() => setShowCloseModal(false)}>Cancelar</Button>
            <Button variant="success" loading={closeMutation.isPending} onClick={() => closeMutation.mutate()}>
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
            placeholder="Describa el trabajo realizado..."
            value={notasCierre}
            onChange={(e) => setNotasCierre(e.target.value)}
          />
        </div>

        {wo.tipo === 'CORRECTIVO' && (
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
            ) : <p className="text-muted" style={{ fontSize: 13 }}>No hay repuestos registrados.</p>}

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
                        value={r.cantidad_usada}
                        onChange={(e) =>
                          setRepuestosUsados((prev) =>
                            prev.map((x) => x.spare_part_id === r.spare_part_id ? { ...x, cantidad_usada: Number(e.target.value) } : x)
                          )
                        }
                        className="form-input"
                        style={{ width: 80 }}
                      />
                      <span style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>{sp?.unidad_medida}</span>
                      <Button variant="ghost" size="sm" onClick={() => setRepuestosUsados((prev) => prev.filter((x) => x.spare_part_id !== r.spare_part_id))}>Quitar</Button>
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
