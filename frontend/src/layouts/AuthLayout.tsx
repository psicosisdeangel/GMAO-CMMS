import React from 'react';
import { Outlet } from 'react-router-dom';

export const AuthLayout: React.FC = () => {
  return (
    <div className="auth-layout">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-icon">⚙</div>
          <h1 className="auth-logo-title">GMAO</h1>
          <p className="auth-logo-subtitle">
            Sistema de Gestión de Mantenimiento
          </p>
        </div>
        <Outlet />
      </div>
    </div>
  );
};
