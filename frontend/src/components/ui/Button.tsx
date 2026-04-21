import React from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost' | 'success';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  children,
  disabled,
  className = '',
  ...props
}) => {
  const baseClass = 'btn';
  const variantClass = `btn-${variant}`;
  const sizeClass = size !== 'md' ? `btn-${size}` : '';

  return (
    <button
      className={`${baseClass} ${variantClass} ${sizeClass} ${className}`.trim()}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="btn-loading">
          <span className="spinner-sm" />
          Cargando...
        </span>
      ) : (
        children
      )}
    </button>
  );
};
