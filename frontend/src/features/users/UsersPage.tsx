import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi, type UserCreatePayload } from '../../api/users';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Spinner } from '../../components/ui/Spinner';
import { Alert } from '../../components/ui/Alert';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import type { User, UserRole } from '../../types/api';

const createSchema = z.object({
  username: z.string().min(3, 'Mínimo 3 caracteres'),
  email: z.string().email('Email inválido'),
  nombre_completo: z.string().min(1, 'El nombre es obligatorio'),
  rol: z.enum(['TECNICO', 'SUPERVISOR']),
  password: z.string().min(8, 'Mínimo 8 caracteres'),
});

type CreateFormData = z.infer<typeof createSchema>;

const UserCreateForm: React.FC<{ onSuccess: () => void; onCancel: () => void }> = ({ onSuccess, onCancel }) => {
  const queryClient = useQueryClient();
  const [serverError, setServerError] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<CreateFormData>({
    defaultValues: { rol: 'TECNICO' },
  });

  const mutation = useMutation({
    mutationFn: (data: UserCreatePayload) => usersApi.create(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['users'] }); onSuccess(); },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: Record<string, string[]> } };
      const d = e.response?.data;
      setServerError(d ? Object.values(d).flat().join('. ') : 'Error al crear usuario.');
    },
  });

  const onSubmit = (data: CreateFormData) => {
    const result = createSchema.safeParse(data);
    if (!result.success) { setServerError('Datos inválidos.'); return; }
    setServerError(null);
    mutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      {serverError && <Alert variant="error" onDismiss={() => setServerError(null)}>{serverError}</Alert>}

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Usuario <span className="required">*</span></label>
          <input className={`form-input ${errors.username ? 'form-input-error' : ''}`} {...register('username')} />
          {errors.username && <span className="form-error">{errors.username.message}</span>}
        </div>
        <div className="form-group">
          <label className="form-label">Rol <span className="required">*</span></label>
          <select className="form-select" {...register('rol')}>
            <option value="TECNICO">Técnico</option>
            <option value="SUPERVISOR">Supervisor</option>
          </select>
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Nombre Completo <span className="required">*</span></label>
        <input className={`form-input ${errors.nombre_completo ? 'form-input-error' : ''}`} {...register('nombre_completo')} />
        {errors.nombre_completo && <span className="form-error">{errors.nombre_completo.message}</span>}
      </div>

      <div className="form-group">
        <label className="form-label">Email <span className="required">*</span></label>
        <input type="email" className={`form-input ${errors.email ? 'form-input-error' : ''}`} {...register('email')} />
        {errors.email && <span className="form-error">{errors.email.message}</span>}
      </div>

      <div className="form-group">
        <label className="form-label">Contraseña <span className="required">*</span></label>
        <input type="password" className={`form-input ${errors.password ? 'form-input-error' : ''}`} {...register('password')} />
        {errors.password && <span className="form-error">{errors.password.message}</span>}
        <span className="form-helper">Mínimo 8 caracteres</span>
      </div>

      <div className="form-actions">
        <Button type="button" variant="secondary" onClick={onCancel}>Cancelar</Button>
        <Button type="submit" variant="primary" loading={mutation.isPending}>Crear Usuario</Button>
      </div>
    </form>
  );
};

export const UsersPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [toggleTarget, setToggleTarget] = useState<User | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['users', page, ''],
    queryFn: () => usersApi.list({ page }),
  });

  const toggleMutation = useMutation({
    mutationFn: (user: User) =>
      usersApi.update(user.id, { is_active: !user.is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setToggleTarget(null);
    },
  });

  if (isLoading) return <Spinner fullPage />;
  if (error) return <div className="page"><Alert variant="error">Error al cargar usuarios.</Alert></div>;

  const totalPages = data ? Math.ceil(data.count / 20) : 1;

  const rolVariant = (rol: UserRole) => rol === 'SUPERVISOR' ? 'info' : 'neutral' as const;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Gestión de Usuarios</h1>
          <p className="page-subtitle">{data?.count ?? 0} usuarios registrados</p>
        </div>
        <Button variant="primary" onClick={() => setShowCreateModal(true)}>+ Nuevo Usuario</Button>
      </div>

      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>Usuario</th>
              <th>Nombre Completo</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Estado</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {data?.results.length === 0 ? (
              <tr><td colSpan={6}>
                <div className="empty-state">
                  <div className="empty-state-icon"></div>
                  <p className="empty-state-title">Sin usuarios registrados</p>
                </div>
              </td></tr>
            ) : data?.results.map((user) => (
              <tr key={user.id}>
                <td><span className="font-mono">{user.username}</span></td>
                <td><strong>{user.nombre_completo}</strong></td>
                <td>{user.email}</td>
                <td><Badge variant={rolVariant(user.rol)}>{user.rol}</Badge></td>
                <td>
                  <Badge variant={user.is_active ? 'success' : 'danger'}>
                    {user.is_active ? 'Activo' : 'Inactivo'}
                  </Badge>
                </td>
                <td>
                  <Button
                    variant={user.is_active ? 'danger' : 'success'}
                    size="sm"
                    onClick={() => setToggleTarget(user)}
                  >
                    {user.is_active ? 'Desactivar' : 'Activar'}
                  </Button>
                </td>
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

      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Nuevo Usuario" size="md">
        <UserCreateForm onSuccess={() => setShowCreateModal(false)} onCancel={() => setShowCreateModal(false)} />
      </Modal>

      <Modal
        isOpen={!!toggleTarget}
        onClose={() => setToggleTarget(null)}
        title={toggleTarget?.is_active ? 'Desactivar usuario' : 'Activar usuario'}
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setToggleTarget(null)}>Cancelar</Button>
            <Button
              variant={toggleTarget?.is_active ? 'danger' : 'success'}
              loading={toggleMutation.isPending}
              onClick={() => toggleTarget && toggleMutation.mutate(toggleTarget)}
            >
              {toggleTarget?.is_active ? 'Desactivar' : 'Activar'}
            </Button>
          </>
        }
      >
        <p>
          ¿Desea {toggleTarget?.is_active ? 'desactivar' : 'activar'} al usuario{' '}
          <strong>{toggleTarget?.username}</strong>?
          {toggleTarget?.is_active && ' El usuario perderá acceso al sistema.'}
        </p>
      </Modal>
    </div>
  );
};
