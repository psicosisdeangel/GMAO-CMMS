import React from 'react';

type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral';

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'neutral',
  children,
  className = '',
}) => {
  return (
    <span className={`badge badge-${variant} ${className}`.trim()}>
      {children}
    </span>
  );
};

// Utility functions to map domain values to badge variants
export const getEstadoBadgeVariant = (
  estado: string
): BadgeVariant => {
  switch (estado) {
    case 'PROGRAMADO':
      return 'info';
    case 'EN_PROCESO':
      return 'warning';
    case 'CERRADA':
      return 'success';
    default:
      return 'neutral';
  }
};

export const getTipoBadgeVariant = (tipo: string): BadgeVariant => {
  switch (tipo) {
    case 'PREVENTIVO':
      return 'info';
    case 'CORRECTIVO':
      return 'danger';
    default:
      return 'neutral';
  }
};

export const getEquipmentEstadoVariant = (estado: string): BadgeVariant => {
  switch (estado.toUpperCase()) {
    case 'ACTIVO':
    case 'OPERATIVO':
      return 'success';
    case 'EN_MANTENIMIENTO':
    case 'MANTENIMIENTO':
      return 'warning';
    case 'INACTIVO':
    case 'FUERA_DE_SERVICIO':
      return 'danger';
    default:
      return 'neutral';
  }
};
