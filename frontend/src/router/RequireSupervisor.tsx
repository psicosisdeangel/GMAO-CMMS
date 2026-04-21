import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const RequireSupervisor: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isSupervisor } = useAuth();

  if (!isSupervisor) {
    return <Navigate to="/work-orders" replace />;
  }

  return <>{children}</>;
};
