import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { equipmentApi } from '../../api/equipment';
import { Button } from '../../components/ui/Button';
import { Alert } from '../../components/ui/Alert';
import type { Equipment } from '../../types/api';

const equipmentSchema = z.object({
  id_unico: z.string().min(1, 'El ID único es obligatorio').max(50),
  nombre: z.string().min(1, 'El nombre es obligatorio').max(200),
  tipo: z.string().min(1, 'El tipo es obligatorio'),
  ubicacion: z.string().min(1, 'La ubicación es obligatoria'),
  fecha_instalacion: z.string().optional(),
  estado: z.string().min(1, 'El estado es obligatorio'),
  descripcion: z.string().optional(),
});

type EquipmentFormData = z.infer<typeof equipmentSchema>;

interface EquipmentFormProps {
  equipment?: Equipment;
  onSuccess: () => void;
  onCancel: () => void;
}

const EQUIPMENT_STATES = [
  { value: 'ACTIVO', label: 'Activo' },
  { value: 'INACTIVO', label: 'Inactivo' },
  { value: 'EN_MANTENIMIENTO', label: 'En Mantenimiento' },
  { value: 'FUERA_DE_SERVICIO', label: 'Fuera de Servicio' },
];

const EQUIPMENT_TYPES = [
  { value: 'MECANICO', label: 'Mecánico' },
  { value: 'ELECTRICO', label: 'Eléctrico' },
  { value: 'HIDRAULICO', label: 'Hidráulico' },
  { value: 'NEUMATICO', label: 'Neumático' },
  { value: 'ELECTRONICO', label: 'Electrónico' },
  { value: 'OTRO', label: 'Otro' },
];

export const EquipmentForm: React.FC<EquipmentFormProps> = ({
  equipment,
  onSuccess,
  onCancel,
}) => {
  const queryClient = useQueryClient();
  const [serverError, setServerError] = useState<string | null>(null);
  const isEditing = !!equipment;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<EquipmentFormData>({
    defaultValues: equipment
      ? {
          id_unico: equipment.id_unico,
          nombre: equipment.nombre,
          tipo: equipment.tipo,
          ubicacion: equipment.ubicacion,
          fecha_instalacion: equipment.fecha_instalacion || '',
          estado: equipment.estado,
          descripcion: equipment.descripcion,
        }
      : { estado: 'ACTIVO' },
  });

  const createMutation = useMutation({
    mutationFn: (data: EquipmentFormData) =>
      equipmentApi.create({
        ...data,
        fecha_instalacion: data.fecha_instalacion || null,
        descripcion: data.descripcion || '',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipment'] });
      onSuccess();
    },
    onError: (err: unknown) => {
      const axiosError = err as {
        response?: { data?: Record<string, string[]> };
      };
      const data = axiosError.response?.data;
      if (data) {
        const msgs = Object.entries(data)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
          .join('. ');
        setServerError(msgs);
      } else {
        setServerError('Error al crear el equipo.');
      }
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: EquipmentFormData) =>
      equipmentApi.update(equipment!.id_unico, {
        nombre: data.nombre,
        tipo: data.tipo,
        ubicacion: data.ubicacion,
        fecha_instalacion: data.fecha_instalacion || null,
        estado: data.estado,
        descripcion: data.descripcion || '',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipment'] });
      onSuccess();
    },
    onError: (err: unknown) => {
      const axiosError = err as {
        response?: { data?: Record<string, string[]> };
      };
      const data = axiosError.response?.data;
      if (data) {
        const msgs = Object.entries(data)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
          .join('. ');
        setServerError(msgs);
      } else {
        setServerError('Error al actualizar el equipo.');
      }
    },
  });

  const onSubmit = (data: EquipmentFormData) => {
    const result = equipmentSchema.safeParse(data);
    if (!result.success) {
      setServerError('Datos inválidos en el formulario.');
      return;
    }
    setServerError(null);
    if (isEditing) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const isLoading = createMutation.isPending || updateMutation.isPending;

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      {serverError && (
        <Alert variant="error" onDismiss={() => setServerError(null)}>
          {serverError}
        </Alert>
      )}

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">
            ID Único <span className="required">*</span>
          </label>
          <input
            className={`form-input ${errors.id_unico ? 'form-input-error' : ''}`}
            placeholder="EQ-001"
            disabled={isEditing}
            {...register('id_unico')}
          />
          {isEditing && (
            <span className="form-helper">El ID único no puede modificarse (REQ-01)</span>
          )}
          {errors.id_unico && (
            <span className="form-error">{errors.id_unico.message}</span>
          )}
        </div>

        <div className="form-group">
          <label className="form-label">
            Nombre <span className="required">*</span>
          </label>
          <input
            className={`form-input ${errors.nombre ? 'form-input-error' : ''}`}
            placeholder="Nombre del equipo"
            {...register('nombre')}
          />
          {errors.nombre && (
            <span className="form-error">{errors.nombre.message}</span>
          )}
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">
            Tipo <span className="required">*</span>
          </label>
          <select
            className={`form-select ${errors.tipo ? 'form-input-error' : ''}`}
            {...register('tipo')}
          >
            <option value="">Seleccionar tipo...</option>
            {EQUIPMENT_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
          {errors.tipo && (
            <span className="form-error">{errors.tipo.message}</span>
          )}
        </div>

        <div className="form-group">
          <label className="form-label">
            Estado <span className="required">*</span>
          </label>
          <select
            className={`form-select ${errors.estado ? 'form-input-error' : ''}`}
            {...register('estado')}
          >
            {EQUIPMENT_STATES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
          {errors.estado && (
            <span className="form-error">{errors.estado.message}</span>
          )}
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">
          Ubicación <span className="required">*</span>
        </label>
        <input
          className={`form-input ${errors.ubicacion ? 'form-input-error' : ''}`}
          placeholder="Ej: Planta 1 — Sector A"
          {...register('ubicacion')}
        />
        {errors.ubicacion && (
          <span className="form-error">{errors.ubicacion.message}</span>
        )}
      </div>

      <div className="form-group">
        <label className="form-label">Fecha de Instalación</label>
        <input
          type="date"
          className="form-input"
          {...register('fecha_instalacion')}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Descripción</label>
        <textarea
          className="form-input form-textarea"
          rows={3}
          placeholder="Descripción opcional del equipo..."
          {...register('descripcion')}
        />
      </div>

      <div className="form-actions">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" variant="primary" loading={isLoading}>
          {isEditing ? 'Guardar Cambios' : 'Crear Equipo'}
        </Button>
      </div>
    </form>
  );
};
