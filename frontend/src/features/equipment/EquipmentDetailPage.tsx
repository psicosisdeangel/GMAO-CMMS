import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { equipmentApi } from '../../api/equipment';
import { workOrdersApi } from '../../api/workOrders';
import { useAuth } from '../../hooks/useAuth';
import { Badge, getEquipmentEstadoVariant, getEstadoBadgeVariant, getTipoBadgeVariant } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Spinner } from '../../components/ui/Spinner';
import { Alert } from '../../components/ui/Alert';
import { EquipmentForm } from './EquipmentForm';

export const EquipmentDetailPage: React.FC = () => {
  const { id_unico } = useParams<{ id_unico: string }>();
  const navigate = useNavigate();
  const { isSupervisor } = useAuth();
  const [showEditModal, setShowEditModal] = useState(false);

  const { data: equipment, isLoading, error, refetch } = useQuery({
    queryKey: ['equipment', id_unico],
    queryFn: () => equipmentApi.getById(id_unico!),
    enabled: !!id_unico,
  });

  const { data: history, isLoading: histLoading } = useQuery({
    queryKey: ['equipment-history', id_unico],
    queryFn: () => workOrdersApi.getEquipmentHistory(id_unico!),
    enabled: !!id_unico,
  });

  if (isLoading) return <Spinner fullPage />;

  if (error || !equipment) {
    return (
      <div className="page">
        <Button variant="ghost" size="sm" onClick={() => navigate('/equipment')} style={{ marginBottom: 16 }}>
          Volver
        </Button>
        <Alert variant="error">Equipo no encontrado o error al cargar.</Alert>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => navigate('/equipment')}>Volver</Button>
          <div>
            <h1 className="page-title">{equipment.nombre}</h1>
            <p className="page-subtitle font-mono">{equipment.id_unico}</p>
          </div>
        </div>
        {isSupervisor && (
          <Button variant="primary" onClick={() => setShowEditModal(true)}>
            Editar Equipo
          </Button>
        )}
      </div>

      {/* Info Card */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">Información del Equipo</h2>
          <Badge variant={getEquipmentEstadoVariant(equipment.estado)}>{equipment.estado}</Badge>
        </div>
        <div className="card-body">
          <div className="detail-grid">
            <div className="detail-field">
              <div className="detail-label">ID Único</div>
              <div className="detail-value font-mono">{equipment.id_unico}</div>
            </div>
            <div className="detail-field">
              <div className="detail-label">Nombre</div>
              <div className="detail-value">{equipment.nombre}</div>
            </div>
            <div className="detail-field">
              <div className="detail-label">Tipo</div>
              <div className="detail-value">{equipment.tipo}</div>
            </div>
            <div className="detail-field">
              <div className="detail-label">Ubicación</div>
              <div className="detail-value">{equipment.ubicacion}</div>
            </div>
            <div className="detail-field">
              <div className="detail-label">Fecha de Instalación</div>
              <div className="detail-value">{equipment.fecha_instalacion ?? '—'}</div>
            </div>
            <div className="detail-field">
              <div className="detail-label">Registrado</div>
              <div className="detail-value">{new Date(equipment.created_at).toLocaleDateString('es-CO')}</div>
            </div>
          </div>
          {equipment.descripcion && (
            <div className="detail-field" style={{ marginTop: 16 }}>
              <div className="detail-label">Descripción</div>
              <div className="detail-value">{equipment.descripcion}</div>
            </div>
          )}
        </div>
      </div>

      {/* History */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Historial de Órdenes de Trabajo</h2>
          <span className="text-muted" style={{ fontSize: 13 }}>{history?.count ?? 0} registros</span>
        </div>
        <div className="card-body" style={{ padding: 0 }}>
          {histLoading ? (
            <div style={{ padding: 20 }}><Spinner size="sm" /></div>
          ) : history?.results.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon"></div>
              <p className="empty-state-title">Sin historial</p>
              <p className="empty-state-text">No hay órdenes de trabajo para este equipo.</p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th>Técnico</th>
                  <th>Fecha Inicio</th>
                  <th>Fecha Cierre</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {history?.results.map((wo) => (
                  <tr key={wo.id_orden}>
                    <td>{wo.id_orden}</td>
                    <td><Badge variant={getTipoBadgeVariant(wo.tipo)}>{wo.tipo}</Badge></td>
                    <td><Badge variant={getEstadoBadgeVariant(wo.estado)}>{wo.estado}</Badge></td>
                    <td>{wo.fk_tecnico_nombre ?? '—'}</td>
                    <td>{new Date(wo.fecha_inicio).toLocaleDateString('es-CO')}</td>
                    <td>{wo.fecha_cierre ? new Date(wo.fecha_cierre).toLocaleDateString('es-CO') : '—'}</td>
                    <td>
                      <Button variant="ghost" size="sm" onClick={() => navigate(`/work-orders/${wo.id_orden}`)}>
                        Ver
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <Modal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        title="Editar Equipo"
        size="lg"
      >
        <EquipmentForm
          equipment={equipment}
          onSuccess={() => { setShowEditModal(false); refetch(); }}
          onCancel={() => setShowEditModal(false)}
        />
      </Modal>
    </div>
  );
};
