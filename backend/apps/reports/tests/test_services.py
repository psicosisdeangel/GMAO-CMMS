"""Tests for ReportsService (REQ-09, REQ-11)."""

import pytest
from django.utils import timezone

from apps.equipment.models import Equipment
from apps.users.models import User
from apps.work_orders.models import WorkOrder


@pytest.fixture
def supervisor(db):
    return User.objects.create_user(
        username="rpt_supervisor",
        password="pass",
        nombre_completo="Supervisor",
        rol="SUPERVISOR",
    )


@pytest.fixture
def equipment(db):
    return Equipment.objects.create(
        id_unico="EQ-RPT-001", nombre="Motor Report", tipo="Motor", ubicacion="Zona D"
    )


@pytest.mark.django_db
class TestReportsService:
    def test_dashboard_returns_expected_keys(self):
        from apps.reports.services.reports_service import ReportsService

        data = ReportsService.get_dashboard_data()
        assert "total_equipos" in data
        assert "ordenes_por_estado" in data
        assert "mttr_ultimos_30_dias_horas" in data
        assert "fallas_por_equipo" in data

    def test_mttr_report_no_data(self):
        from apps.reports.services.reports_service import ReportsService

        data = ReportsService.get_mttr_report(month="2000-01")
        assert data["total_ordenes_correctivas_cerradas"] == 0
        assert data["mttr_horas"] is None

    def test_mttr_report_with_data(self, supervisor, equipment):
        from apps.reports.services.reports_service import ReportsService

        now = timezone.now()
        # Create a closed corrective order in the current month
        WorkOrder.objects.create(
            tipo="CORRECTIVO",
            estado="CERRADA",
            descripcion="Test",
            fecha_inicio=now - timezone.timedelta(hours=2),
            fecha_cierre=now,
            fk_equipo=equipment,
            fk_tecnico=supervisor,
        )
        month_str = now.strftime("%Y-%m")
        data = ReportsService.get_mttr_report(month=month_str)
        assert data["total_ordenes_correctivas_cerradas"] == 1
        assert data["mttr_horas"] is not None
        assert data["mttr_horas"] > 0


@pytest.mark.django_db
class TestDashboardController:
    def test_dashboard_supervisor_access(self, supervisor):
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=supervisor)
        response = client.get("/api/reports/dashboard/")
        assert response.status_code == 200

    def test_dashboard_tecnico_forbidden(self, db):
        from rest_framework.test import APIClient

        from apps.users.models import User

        tecnico = User.objects.create_user(
            username="rpt_tecnico",
            password="pass",
            nombre_completo="Tecnico",
            rol="TECNICO",
        )
        client = APIClient()
        client.force_authenticate(user=tecnico)
        response = client.get("/api/reports/dashboard/")
        assert response.status_code == 403
