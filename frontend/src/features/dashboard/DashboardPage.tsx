import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { reportsApi } from '../../api/reports';
import { Spinner } from '../../components/ui/Spinner';
import { Alert } from '../../components/ui/Alert';

export const DashboardPage: React.FC = () => {
  const [mttrMonth, setMttrMonth] = useState<string>(
    () => new Date().toISOString().slice(0, 7)
  );

  const {
    data: dashboard,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => reportsApi.getDashboard(),
    refetchInterval: 3000,
  });

  const { data: mttr, isLoading: mttrLoading } = useQuery({
    queryKey: ['mttr', mttrMonth],
    queryFn: () => reportsApi.getMttr(mttrMonth),
    enabled: !!mttrMonth,
  });

  if (isLoading) return <Spinner fullPage />;

  if (error) {
    return (
      <div className="page">
        <Alert variant="error" title="Error al cargar el dashboard">
          No se pudieron cargar los datos. Verifique la conexión al servidor.
        </Alert>
      </div>
    );
  }

  const estadoLabels: Record<string, string> = {
    PROGRAMADO: 'Programadas',
    EN_PROCESO: 'En Proceso',
    CERRADA: 'Cerradas',
  };

  const estadoColors: Record<string, string> = {
    PROGRAMADO: 'var(--color-info)',
    EN_PROCESO: 'var(--color-warning)',
    CERRADA: 'var(--color-success)',
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard de Supervisión</h1>
          <p className="page-subtitle">
            Resumen en tiempo real del sistema de mantenimiento
          </p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => refetch()}>
          ↺ Actualizar
        </button>
      </div>

      {/* KPI Cards */}
      <div className="dashboard-grid">
        <div className="kpi-card kpi-card-primary">
          <div className="kpi-icon">🏭</div>
          <div className="kpi-content">
            <span className="kpi-label">Total Equipos</span>
            <span className="kpi-value">{dashboard?.total_equipos ?? 0}</span>
          </div>
        </div>

        {dashboard?.ordenes_por_estado &&
          Object.entries(dashboard.ordenes_por_estado).map(
            ([estado, count]) => (
              <div
                key={estado}
                className="kpi-card"
                style={{
                  borderLeftColor: estadoColors[estado] || 'var(--color-primary)',
                }}
              >
                <div className="kpi-icon">📋</div>
                <div className="kpi-content">
                  <span className="kpi-label">
                    {estadoLabels[estado] || estado}
                  </span>
                  <span className="kpi-value">{count}</span>
                </div>
              </div>
            )
          )}

        <div className="kpi-card kpi-card-warning">
          <div className="kpi-icon">⏱</div>
          <div className="kpi-content">
            <span className="kpi-label">MTTR (horas)</span>
            <span className="kpi-value">
              {dashboard?.mttr_ultimos_30_dias_horas != null
                ? dashboard.mttr_ultimos_30_dias_horas.toFixed(1)
                : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {/* Second row */}
      <div className="dashboard-row">
        {/* Fallas por equipo */}
        <div className="card card-half">
          <div className="card-header">
            <h2 className="card-title">Fallas por Equipo</h2>
          </div>
          <div className="card-body">
            {!dashboard?.fallas_por_equipo?.length ? (
              <p className="text-muted text-center">
                Sin datos de fallas registradas
              </p>
            ) : (
              <div className="fallas-list">
                {dashboard.fallas_por_equipo.map((item, idx) => (
                  <div key={idx} className="fallas-item">
                    <span className="fallas-equipo">{item.equipo_nombre}</span>
                    <div className="fallas-bar-wrapper">
                      <div
                        className="fallas-bar"
                        style={{
                          width: `${Math.min(
                            (item.total_fallas /
                              Math.max(
                                ...dashboard.fallas_por_equipo.map(
                                  (f) => f.total_fallas
                                )
                              )) *
                              100,
                            100
                          )}%`,
                        }}
                      />
                    </div>
                    <span className="fallas-count">{item.total_fallas}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* MTTR por mes */}
        <div className="card card-half">
          <div className="card-header">
            <h2 className="card-title">Reporte MTTR Mensual</h2>
          </div>
          <div className="card-body">
            <div className="form-group">
              <label className="form-label">Seleccionar Mes</label>
              <input
                type="month"
                className="form-input"
                value={mttrMonth}
                onChange={(e) => setMttrMonth(e.target.value)}
              />
            </div>

            {mttrLoading ? (
              <Spinner size="sm" />
            ) : mttr ? (
              <div className="mttr-stats">
                <div className="mttr-stat">
                  <span className="mttr-stat-label">MTTR (horas)</span>
                  <span className="mttr-stat-value">
                    {mttr.mttr_horas != null
                      ? mttr.mttr_horas.toFixed(2)
                      : 'N/A'}
                  </span>
                </div>
                <div className="mttr-stat">
                  <span className="mttr-stat-label">Correctivos Cerrados</span>
                  <span className="mttr-stat-value">
                    {mttr.total_ordenes_correctivas_cerradas}
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-muted">Sin datos para el mes seleccionado</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
