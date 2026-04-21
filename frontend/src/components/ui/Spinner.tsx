import React from 'react';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  fullPage?: boolean;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  className = '',
  fullPage = false,
}) => {
  const spinner = (
    <div className={`spinner spinner-${size} ${className}`.trim()} />
  );

  if (fullPage) {
    return (
      <div className="spinner-fullpage">
        {spinner}
        <span className="spinner-text">Cargando...</span>
      </div>
    );
  }

  return spinner;
};
