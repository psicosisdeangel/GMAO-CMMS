"""Controller tests for work orders — covers EQ-04: PATCH on CERRADA → 422."""

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.equipment.models import Equipment
from apps.users.models import User
from apps.work_orders.models import WorkOrder


@pytest.fixture
def supervisor(db):
    return User.objects.create_user(
        username="wo_ctrl_sup",
        password="pass",
        nombre_completo="Supervisor",
        rol="SUPERVISOR",
    )


@pytest.fixture
def tecnico(db):
    return User.objects.create_user(
        username="wo_ctrl_tec",
        password="pass",
        nombre_completo="Tecnico",
        rol="TECNICO",
    )


@pytest.fixture
def equipment(db):
    return Equipment.objects.create(
        id_unico="EQ-CTRL-WO",
        nombre="Test Motor",
        tipo="Motor",
        ubicacion="Zona B",
    )


@pytest.fixture
def supervisor_client(supervisor):
    c = APIClient()
    c.force_authenticate(user=supervisor)
    return c


@pytest.fixture
def tecnico_client(tecnico):
    c = APIClient()
    c.force_authenticate(user=tecnico)
    return c


@pytest.fixture
def closed_order(supervisor, equipment):
    order = WorkOrder.objects.create(
        tipo="CORRECTIVO",
        estado="CERRADA",
        descripcion="Orden cerrada de prueba",
        fecha_inicio=timezone.now(),
        fecha_cierre=timezone.now(),
        fk_equipo=equipment,
        fk_tecnico=supervisor,
    )
    return order


@pytest.mark.django_db
class TestWorkOrderControllers:
    def test_create_correctivo_tecnico(self, tecnico_client, equipment):
        response = tecnico_client.post(
            "/api/work-orders/",
            {
                "tipo": "CORRECTIVO",
                "descripcion": "Falla",
                "fecha_inicio": timezone.now().isoformat(),
                "fk_equipo_id": equipment.id_unico,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_tecnico_cannot_create_preventivo(self, tecnico_client, equipment):
        future = (timezone.now() + timezone.timedelta(days=7)).isoformat()
        response = tecnico_client.post(
            "/api/work-orders/",
            {
                "tipo": "PREVENTIVO",
                "descripcion": "Mantenimiento",
                "fecha_inicio": future,
                "fk_equipo_id": equipment.id_unico,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_patch_closed_order_returns_422(self, supervisor_client, closed_order):
        """EQ-04: PATCH on CERRADA → 422 (REQ-05)."""
        response = supervisor_client.patch(
            f"/api/work-orders/{closed_order.id_orden}/",
            {"descripcion": "Intento de modificación"},
            format="json",
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_close_already_closed_returns_422(self, supervisor_client, closed_order):
        """REQ-05: closing an already-closed order → 422."""
        response = supervisor_client.post(
            f"/api/work-orders/{closed_order.id_orden}/close/",
            {"notas_cierre": ""},
            format="json",
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_tecnico_only_sees_own_orders(self, tecnico_client, tecnico, equipment):
        # Tecnico's order
        WorkOrder.objects.create(
            tipo="CORRECTIVO",
            estado="EN_PROCESO",
            descripcion="Own",
            fecha_inicio=timezone.now(),
            fk_equipo=equipment,
            fk_tecnico=tecnico,
        )
        response = tecnico_client.get("/api/work-orders/")
        assert response.status_code == status.HTTP_200_OK
        for order in response.data["results"]:
            assert order["fk_tecnico"] == tecnico.id
