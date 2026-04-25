import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { equipmentApi } from '../../api/equipment';
import { useAuth } from '../../hooks/useAuth';
import { Badge, getEquipmentEstadoVariant } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Spinner } from '../../components/ui/Spinner';
import { Alert } from '../../components/ui/Alert';
import { EquipmentForm } from './EquipmentForm';

export const EquipmentListPage: React.FC = () => {
  const navigate = useNavigate();
  const { isSupervisor } = useAuth();
  const queryClient = useQueryClient();

  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['equipment', page, search],
    queryFn: () => equipmentApi.list({ page, search: search || undefined }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => equipmentApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipment'] });
      setDeleteTarget(null);
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { error?: string } } };
      setDeleteError(e.response?.data?.error || 'No se pudo eliminar el equipo.');
    },
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearch(searchInput);
    setPage(1);
  };

  if (isLoading) return <Spinner fullPage />;

  if (error) {
    return (
      <div className="page">
        <Alert variant="error">Error al cargar equipos. Verifique la conexión al servidor.</Alert>
      </div>
    );
  }

  const totalPages = data ? Math.ceil(data.count / 20) : 1;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Equipos</h1>
          <p className="page-subtitle">{data?.count ?? 0} equipos registrados</p>
        </div>
        <div className="page-actions">
          {isSupervisor && (
            <Button variant="primary" onClick={() => setShowCreateModal(true)}>
              + Nuevo Equipo
            </Button>
          )}
        </div>
      </div>

      {/* Search */}
      <div className="filters-bar">
        <form onSubmit={handleSearch} className="flex gap-2" style={{ flex: 1 }}>
          <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
            <input
              className="form-input"
              placeholder="Buscar por nombre, tipo o ubicación..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
          </div>
          <Button type="submit" variant="secondary">Buscar</Button>
          {search && (
            <Button
              type="button"
              variant="ghost"
              onClick={() => { setSearch(''); setSearchInput(''); setPage(1); }}
            >
              Limpiar
            </Button>
          )}
        </form>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>ID Único</th>
              <th>Nombre</th>
              <th>Tipo</th>
              <th>Ubicación</th>
              <th>Estado</th>
              <th>Instalación</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {data?.results.length === 0 ? (
              <tr>
                <td colSpan={7}>
                  <div className="empty-state">
                    <div className="empty-state-icon"></div>
                    <p className="empty-state-title">Sin equipos registrados</p>
                    <p className="empty-state-text">
                      {isSupervisor ? 'Cree el primer equipo pulsando "+ Nuevo Equipo"' : 'No hay equipos disponibles.'}
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              data?.results.map((eq) => (
                <tr key={eq.id_unico}>
                  <td><span className="font-mono">{eq.id_unico}</span></td>
                  <td><strong>{eq.nombre}</strong></td>
                  <td>{eq.tipo}</td>
                  <td>{eq.ubicacion}</td>
                  <td>
                    <Badge variant={getEquipmentEstadoVariant(eq.estado)}>
                      {eq.estado}
                    </Badge>
                  </td>
                  <td>{eq.fecha_instalacion ?? '—'}</td>
                  <td>
                    <div className="table-actions">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/equipment/${eq.id_unico}`)}
                      >
                        Ver
                      </Button>
                      {isSupervisor && (
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => { setDeleteTarget(eq.id_unico); setDeleteError(null); }}
                        >
                          Eliminar
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="pagination">
            <span className="pagination-info">
              Página {page} de {totalPages} ({data?.count} total)
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

      {/* Create Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Nuevo Equipo"
        size="lg"
      >
        <EquipmentForm
          onSuccess={() => setShowCreateModal(false)}
          onCancel={() => setShowCreateModal(false)}
        />
      </Modal>

      {/* Delete Confirm Modal */}
      <Modal
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        title="Confirmar eliminación"
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setDeleteTarget(null)}>Cancelar</Button>
            <Button
              variant="danger"
              loading={deleteMutation.isPending}
              onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget)}
            >
              Eliminar
            </Button>
          </>
        }
      >
        {deleteError && <Alert variant="error">{deleteError}</Alert>}
        <p>¿Está seguro de que desea eliminar el equipo <strong>{deleteTarget}</strong>? Esta acción no se puede deshacer.</p>
      </Modal>
    </div>
  );
};
