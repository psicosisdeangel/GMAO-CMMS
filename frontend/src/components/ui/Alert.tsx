import React from 'react';

type AlertVariant = 'success' | 'error' | 'warning' | 'info';

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: React.ReactNode;
  onDismiss?: () => void;
  className?: string;
  style?: React.CSSProperties;
}

export const Alert: React.FC<AlertProps> = ({
  variant = 'info',
  title,
  children,
  onDismiss,
  className = '',
  style,
}) => {
  const icons: Record<AlertVariant, string> = {
    success: 'OK',
    error: 'Error',
    warning: 'Aviso',
    info: 'Info',
  };

  return (
    <div className={`alert alert-${variant} ${className}`.trim()} role="alert" style={style}>
      <span className="alert-icon">{icons[variant]}</span>
      <div className="alert-content">
        {title && <strong className="alert-title">{title}</strong>}
        <span>{children}</span>
      </div>
      {onDismiss && (
        <button
          className="alert-close"
          onClick={onDismiss}
          aria-label="Cerrar"
        >
          x
        </button>
      )}
    </div>
  );
};
