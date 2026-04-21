import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { usePermissions } from '../hooks/usePermissions';

interface NavItem {
  to: string;
  label: string;
  icon: string;
  supervisorOnly?: boolean;
}

const navItems: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊', supervisorOnly: true },
  { to: '/equipment', label: 'Equipos', icon: '🏭' },
  { to: '/work-orders', label: 'Órdenes de Trabajo', icon: '📋' },
  { to: '/inventory', label: 'Inventario', icon: '📦' },
  { to: '/users', label: 'Usuarios', icon: '👥', supervisorOnly: true },
  { to: '/audit', label: 'Auditoría', icon: '🔍', supervisorOnly: true },
];

export const AppLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const { canViewDashboard, canManageUsers } = usePermissions();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const visibleItems = navItems.filter((item) => {
    if (!item.supervisorOnly) return true;
    if (item.to === '/dashboard') return canViewDashboard;
    if (item.to === '/users') return canManageUsers;
    if (item.to === '/audit') return canManageUsers;
    return canViewDashboard;
  });

  return (
    <div className="app-layout">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <span className="sidebar-logo-icon">⚙</span>
            <div>
              <span className="sidebar-logo-text">GMAO</span>
              <span className="sidebar-logo-sub">Mantenimiento</span>
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {visibleItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'sidebar-link-active' : ''}`
              }
              onClick={() => setSidebarOpen(false)}
            >
              <span className="sidebar-link-icon">{item.icon}</span>
              <span className="sidebar-link-label">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-user-avatar">
              {user?.nombre_completo?.[0]?.toUpperCase() ||
                user?.username?.[0]?.toUpperCase() ||
                '?'}
            </div>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">
                {user?.nombre_completo || user?.username}
              </span>
              <span className="sidebar-user-role">{user?.rol}</span>
            </div>
          </div>
          <button className="sidebar-logout" onClick={handleLogout}>
            <span>⬅</span> Salir
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="main-wrapper">
        {/* Top bar for mobile */}
        <header className="topbar">
          <button
            className="topbar-menu-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle menu"
          >
            ☰
          </button>
          <span className="topbar-title">GMAO</span>
          <span className="topbar-user">{user?.nombre_completo}</span>
        </header>

        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
