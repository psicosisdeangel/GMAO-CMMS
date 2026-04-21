import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppLayout } from '../layouts/AppLayout';
import { AuthLayout } from '../layouts/AuthLayout';
import { LoginPage } from '../features/auth/LoginPage';
import { SignUpPage } from '../features/auth/SignUpPage';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { EquipmentListPage } from '../features/equipment/EquipmentListPage';
import { EquipmentDetailPage } from '../features/equipment/EquipmentDetailPage';
import { WorkOrderListPage } from '../features/work-orders/WorkOrderListPage';
import { WorkOrderDetailPage } from '../features/work-orders/WorkOrderDetailPage';
import { InventoryListPage } from '../features/inventory/InventoryListPage';
import { UsersPage } from '../features/users/UsersPage';
import { AuditPage } from '../features/audit/AuditPage';
import { RequireAuth } from './RequireAuth';
import { RequireSupervisor } from './RequireSupervisor';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AuthLayout />,
    children: [
      { index: true, element: <Navigate to="/login" replace /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <SignUpPage /> },
    ],
  },
  {
    path: '/',
    element: (
      <RequireAuth>
        <AppLayout />
      </RequireAuth>
    ),
    children: [
      {
        path: 'dashboard',
        element: (
          <RequireSupervisor>
            <DashboardPage />
          </RequireSupervisor>
        ),
      },
      { path: 'equipment', element: <EquipmentListPage /> },
      { path: 'equipment/:id_unico', element: <EquipmentDetailPage /> },
      { path: 'work-orders', element: <WorkOrderListPage /> },
      { path: 'work-orders/:id', element: <WorkOrderDetailPage /> },
      { path: 'inventory', element: <InventoryListPage /> },
      {
        path: 'users',
        element: (
          <RequireSupervisor>
            <UsersPage />
          </RequireSupervisor>
        ),
      },
      {
        path: 'audit',
        element: (
          <RequireSupervisor>
            <AuditPage />
          </RequireSupervisor>
        ),
      },
      { path: '*', element: <Navigate to="/work-orders" replace /> },
    ],
  },
]);
