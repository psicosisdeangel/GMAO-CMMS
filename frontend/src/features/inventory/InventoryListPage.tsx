import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { inventoryApi, type SparePartCreatePayload } from '../../api/inventory';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Spinner } from '../../components/ui/Spinner';
import { Alert } from '../../components/ui/Alert';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import type { SparePart } from '../../types/api';

const sparePartSchema = z.object({
  nombre: z.string().min(1, 'El nombre es obligatorio'),
  codigo: z.string().min(1, 'El código es obligatorio'),
  descripcion: z.string().optional(),
  cantidad_stock: z.coerce.number().min(0, 'Debe ser 0 o mayor'),
  unidad_medida: z.string().min(1, 'La unidad es obligatoria'),
});

type SPFormData = z.infer<typeof sparePartSchema>;

const SparePartForm: React.FC<{
  sparePart?: SparePart;
  onSuccess: () => void;
  onCancel: () => void;
}> = ({ sparePart, onSuccess, onCancel }) => {
  const queryClient = useQueryClient();
  const [serverError, setServerError] = useState<string | null>(null);
  const isEditing = !!sparePart;

  const { register, handleSubmit, formState: { errors } } = useForm<SPFormData>({
    defaultValues: sparePart
      ? { nombre: sparePart.nombre, codigo: sparePart.codigo, descripcion: sparePart.descripcion, cantidad_stock: sparePart.cantidad_stock, unidad_medida: sparePart.unidad_medida }
      : { unidad_medida: 'unidades', cantidad_stock: 0 },
  });

  const createMutation = useMutation({
    mutationFn: (data: SparePartCreatePayload) => inventoryApi.create(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['inventory'] }); onSuccess(); },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: Record<string, string[]> } };
      const d = e.response?.data;
      setServerError(d ? Object.values(d).flat().join('. ') : 'Error al crear repuesto.');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: Partial<SparePartCreatePayload>) => inventoryApi.update(sparePart!.id_repuesto, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['inventory'] }); onSuccess(); },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: Record<string, string[]> } };
      const d = e.response?.data;
      setServerError(d ? Object.values(d).flat().join('. ') : 'Error al actualizar repuesto.');
    },
  });

  const onSubmit = (data: SPFormData) => {
    const result = sparePartSchema.safeParse(data);
    if (!result.success) { setServerError('Datos inválidos.'); return; }
    setServerError(null);
    const payload = { ...data, descripcion: data.descripcion ?? '' };
    if (isEditing) updateMutation.mutate(payload);
    else createMutation.mutate(payload);
  };

  const isLoading = createMutation.isPending || updateMutation.isPending;

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      {serverError && <Alert variant="error" onDismiss={() => setServerError(null)}>{serverError}</Alert>}

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Nombre <span className="required">*</span></label>
          <input className={`form-input ${errors.nombre ? 'form-input-error' : ''}`} {...register('nombre')} />
          {errors.nombre && <span className="form-error">{errors.nombre.message}</span>}
        </div>
        <div className="form-group">
          <label className="form-label">Código <span className="required">*</span></label>
          <input className={`form-input ${errors.codigo ? 'form-input-error' : ''}`} {...register('codigo')} />
          {errors.codigo && <span className="form-error">{errors.codigo.message}</span>}
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Stock <span className="required">*</span></label>
          <input type="number" min="0" className={`form-input ${errors.cantidad_stock ? 'form-input-error' : ''}`} {...register('cantidad_stock')} />
          {errors.cantidad_stock && <span className="form-error">{errors.cantidad_stock.message}</span>}
        </div>
        <div className="form-group">
          <label className="form-label">Unidad</label>
          <input className="form-input" placeholder="unidades, kg, litros..." {...register('unidad_medida')} />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Descripción</label>
        <textarea className="form-input form-textarea" rows={2} {...register('descripcion')} />
      </div>

      <div className="form-actions">
        <Button type="button" variant="secondary" onClick={onCancel}>Cancelar</Button>
        <Button type="submit" variant="primary" loading={isLoading}>
          {isEditing ? 'Guardar' : 'Agregar Repuesto'}
        </Button>
      </div>
    </form>
  );
};

export const InventoryListPage: React.FC = () => {
  const { isSupervisor } = useAuth();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editTarget, setEditTarget] = useState<SparePart | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['inventory', page, search],
    queryFn: () => inventoryApi.list({ page, search: search || undefined }),
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearch(searchInput);
    setPage(1);
  };

  if (isLoading) return <Spinner fullPage />;
  if (error) return <div className="page"><Alert variant="error">Error al cargar inventario.</Alert></div>;

  const totalPages = data ? Math.ceil(data.count / 20) : 1;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Inventario de Repuestos</h1>
          <p className="page-subtitle">{data?.count ?? 0} repuestos registrados</p>
        </div>
        {isSupervisor && (
          <Button variant="primary" onClick={() => setShowCreateModal(true)}>+ Agregar Repuesto</Button>
        )}
      </div>

      <div className="filters-bar">
        <form onSubmit={handleSearch} className="flex gap-2" style={{ flex: 1 }}>
          <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
            <input className="form-input" placeholder="Buscar por nombre o código..." value={searchInput} onChange={(e) => setSearchInput(e.target.value)} />
          </div>
          <Button type="submit" variant="secondary">Buscar</Button>
          {search && <Button type="button" variant="ghost" onClick={() => { setSearch(''); setSearchInput(''); }}>Limpiar</Button>}
        </form>
      </div>

      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Nombre</th>
              <th>Stock</th>
              <th>Unidad</th>
              <th>Descripción</th>
              {isSupervisor && <th></th>}
            </tr>
          </thead>
          <tbody>
            {data?.results.length === 0 ? (
              <tr><td colSpan={6}>
                <div className="empty-state">
                  <div className="empty-state-icon"></div>
                  <p className="empty-state-title">Sin repuestos registrados</p>
                </div>
              </td></tr>
            ) : data?.results.map((sp) => (
              <tr key={sp.id_repuesto}>
                <td><span className="font-mono">{sp.codigo}</span></td>
                <td><strong>{sp.nombre}</strong></td>
                <td>
                  <span style={{ color: sp.cantidad_stock === 0 ? 'var(--color-danger)' : sp.cantidad_stock < 5 ? 'var(--color-warning)' : 'var(--color-success)', fontWeight: 700 }}>
                    {sp.cantidad_stock}
                  </span>
                </td>
                <td>{sp.unidad_medida}</td>
                <td className="text-muted" style={{ fontSize: 12 }}>{sp.descripcion || '—'}</td>
                {isSupervisor && (
                  <td>
                    <Button variant="ghost" size="sm" onClick={() => setEditTarget(sp)}>Editar</Button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>

        {totalPages > 1 && (
          <div className="pagination">
            <span className="pagination-info">Página {page} de {totalPages}</span>
            <div className="pagination-controls">
              <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Anterior</Button>
              <Button variant="secondary" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Siguiente</Button>
            </div>
          </div>
        )}
      </div>

      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Agregar Repuesto" size="md">
        <SparePartForm onSuccess={() => setShowCreateModal(false)} onCancel={() => setShowCreateModal(false)} />
      </Modal>

      <Modal isOpen={!!editTarget} onClose={() => setEditTarget(null)} title="Editar Repuesto" size="md">
        {editTarget && (
          <SparePartForm sparePart={editTarget} onSuccess={() => setEditTarget(null)} onCancel={() => setEditTarget(null)} />
        )}
      </Modal>
    </div>
  );
};
