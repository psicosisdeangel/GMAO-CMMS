import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { workOrdersApi, type WorkOrderCreatePayload } from '../../api/workOrders';
import { equipmentApi } from '../../api/equipment';
import { usersApi } from '../../api/users';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../../components/ui/Button';
import { Alert } from '../../components/ui/Alert';

const workOrderSchema = z.object({
  tipo: z.enum(['PREVENTIVO', 'CORRECTIVO']),
  descripcion: z.string().min(1, 'La descripción es obligatoria'),
  fecha_inicio: z.string().min(1, 'La fecha es obligatoria'),
  frecuencia: z.enum(['UNICA', 'MENSUAL', 'TRIMESTRAL', 'ANUAL']),
  fk_equipo_id_id: z.string().min(1, 'Seleccione un equipo'),
  fk_tecnico_id_id: z.string().optional(),
});

type WOFormData = z.infer<typeof workOrderSchema>;

interface WorkOrderFormProps {
  defaultEquipoId?: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export const WorkOrderForm: React.FC<WorkOrderFormProps> = ({
  defaultEquipoId,
  onSuccess,
  onCancel,
}) => {
  const queryClient = useQueryClient();
  const { isSupervisor, user } = useAuth();
  const [serverError, setServerError] = useState<string | null>(null);

  const { data: equipmentData } = useQuery({
    queryKey: ['equipment', 1, ''],
    queryFn: () => equipmentApi.list({ page: 1 }),
  });

  const { data: usersData } = useQuery({
    queryKey: ['users', 1, ''],
    queryFn: () => usersApi.list({ page: 1 }),
    enabled: isSupervisor,
  });

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<WOFormData>({
    defaultValues: {
      tipo: 'CORRECTIVO',
      frecuencia: 'UNICA',
      fk_equipo_id_id: defaultEquipoId ?? '',
      fk_tecnico_id_id: isSupervisor ? '' : String(user?.id ?? ''),
    },
  });

  const tipoValue = watch('tipo');

  const createMutation = useMutation({
    mutationFn: (data: WorkOrderCreatePayload) => workOrdersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-orders'] });
      onSuccess();
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: Record<string, string[]> } };
      const d = e.response?.data;
      if (d) {
        const msgs = Object.entries(d)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
          .join('. ');
        setServerError(msgs);
      } else {
        setServerError('Error al crear la orden de trabajo.');
      }
    },
  });

  const onSubmit = (data: WOFormData) => {
    const result = workOrderSchema.safeParse(data);
    if (!result.success) {
      setServerError('Datos del formulario inválidos.');
      return;
    }
    setServerError(null);
    const payload: WorkOrderCreatePayload = {
      tipo: data.tipo,
      descripcion: data.descripcion,
      fecha_inicio: data.fecha_inicio,
      frecuencia: data.frecuencia,
      fk_equipo_id_id: data.fk_equipo_id_id,
      fk_tecnico_id_id: data.fk_tecnico_id_id ? Number(data.fk_tecnico_id_id) : null,
    };
    createMutation.mutate(payload);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      {serverError && (
        <Alert variant="error" onDismiss={() => setServerError(null)}>{serverError}</Alert>
      )}

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Tipo <span className="required">*</span></label>
          <select className={`form-select ${errors.tipo ? 'form-input-error' : ''}`} {...register('tipo')}>
            <option value="CORRECTIVO">Correctivo</option>
            {isSupervisor && <option value="PREVENTIVO">Preventivo</option>}
          </select>
          {errors.tipo && <span className="form-error">{errors.tipo.message}</span>}
        </div>

        {tipoValue === 'PREVENTIVO' && isSupervisor && (
          <div className="form-group">
            <label className="form-label">Frecuencia</label>
            <select className="form-select" {...register('frecuencia')}>
              <option value="UNICA">Única</option>
              <option value="MENSUAL">Mensual</option>
              <option value="TRIMESTRAL">Trimestral</option>
              <option value="ANUAL">Anual</option>
            </select>
          </div>
        )}
      </div>

      <div className="form-group">
        <label className="form-label">Equipo <span className="required">*</span></label>
        <select
          className={`form-select ${errors.fk_equipo_id ? 'form-input-error' : ''}`}
          {...register('fk_equipo_id')}
        >
          <option value="">Seleccionar equipo...</option>
          {equipmentData?.results.map((eq) => (
            <option key={eq.id_unico} value={eq.id_unico}>
              {eq.id_unico} — {eq.nombre}
            </option>
          ))}
        </select>
        {errors.fk_equipo_id && <span className="form-error">{errors.fk_equipo_id.message}</span>}
      </div>

      <div className="form-group">
        <label className="form-label">Descripción <span className="required">*</span></label>
        <textarea
          className={`form-input form-textarea ${errors.descripcion ? 'form-input-error' : ''}`}
          rows={3}
          placeholder="Describa el trabajo a realizar..."
          {...register('descripcion')}
        />
        {errors.descripcion && <span className="form-error">{errors.descripcion.message}</span>}
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Fecha Inicio <span className="required">*</span></label>
          <input
            type="datetime-local"
            className={`form-input ${errors.fecha_inicio ? 'form-input-error' : ''}`}
            {...register('fecha_inicio')}
          />
          {errors.fecha_inicio && <span className="form-error">{errors.fecha_inicio.message}</span>}
        </div>

        {isSupervisor && (
          <div className="form-group">
            <label className="form-label">Técnico Asignado</label>
            <select className="form-select" {...register('fk_tecnico_id')}>
              <option value="">Sin asignar</option>
              {usersData?.results
                .filter((u) => u.is_active)
                .map((u) => (
                  <option key={u.id} value={String(u.id)}>
                    {u.nombre_completo} ({u.rol})
                  </option>
                ))}
            </select>
          </div>
        )}
      </div>

      <div className="form-actions">
        <Button type="button" variant="secondary" onClick={onCancel}>Cancelar</Button>
        <Button type="submit" variant="primary" loading={createMutation.isPending}>
          Crear Orden
        </Button>
      </div>
    </form>
  );
};
