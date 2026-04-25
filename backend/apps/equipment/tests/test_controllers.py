"""Controller tests for equipment app.

Covers scenario EQ-01: TECNICO trying POST (SUPERVISOR-only) → 403.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture
def supervisor(db):
    return User.objects.create_user(
        username="eq_ctrl_sup",
        password="pass",
        nombre_completo="Supervisor",
        rol="SUPERVISOR",
    )


@pytest.fixture
def tecnico(db):
    return User.objects.create_user(
        username="eq_ctrl_tec",
        password="pass",
        nombre_completo="Tecnico",
        rol="TECNICO",
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
def equipment_payload():
    return {
        "id_unico": "EQ-CTRL-001",
        "nombre": "Bomba Hidráulica",
        "tipo": "Bomba",
        "ubicacion": "Sala 1",
        "descripcion": "",
    }


@pytest.mark.django_db
class TestEquipmentListCreate:
    def test_tecnico_can_list_equipment(self, tecnico_client):
        response = tecnico_client.get("/api/equipment/")
        assert response.status_code == status.HTTP_200_OK

    def test_supervisor_can_create_equipment(self, supervisor_client, equipment_payload):
        response = supervisor_client.post("/api/equipment/", equipment_payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id_unico"] == "EQ-CTRL-001"

    def test_tecnico_cannot_create_equipment(self, tecnico_client, equipment_payload):
        """EQ-01: TECNICO → 403 on POST."""
        response = tecnico_client.post("/api/equipment/", equipment_payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_duplicate_id_returns_409(self, supervisor_client, equipment_payload):
        supervisor_client.post("/api/equipment/", equipment_payload, format="json")
        response = supervisor_client.post("/api/equipment/", equipment_payload, format="json")
        assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.django_db
class TestEquipmentDetail:
    def test_patch_id_unico_returns_400(self, supervisor_client, equipment_payload):
        """REQ-01: any attempt to change id_unico → 400."""
        supervisor_client.post("/api/equipment/", equipment_payload, format="json")
        response = supervisor_client.patch(
            "/api/equipment/EQ-CTRL-001/",
            {"id_unico": "EQ-NEW"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_detail_success(self, supervisor_client, equipment_payload):
        supervisor_client.post("/api/equipment/", equipment_payload, format="json")
        response = supervisor_client.get("/api/equipment/EQ-CTRL-001/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id_unico"] == "EQ-CTRL-001"

    def test_get_detail_not_found(self, supervisor_client):
        response = supervisor_client.get("/api/equipment/GHOST-999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_equipment_success(self, supervisor_client, equipment_payload):
        supervisor_client.post("/api/equipment/", equipment_payload, format="json")
        response = supervisor_client.patch(
            "/api/equipment/EQ-CTRL-001/",
            {"nombre": "Bomba Actualizada"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["nombre"] == "Bomba Actualizada"

    def test_patch_equipment_not_found(self, supervisor_client):
        response = supervisor_client.patch(
            "/api/equipment/GHOST-999/",
            {"nombre": "X"},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_equipment_success(self, supervisor_client, equipment_payload):
        supervisor_client.post("/api/equipment/", equipment_payload, format="json")
        response = supervisor_client.delete("/api/equipment/EQ-CTRL-001/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_equipment_not_found(self, supervisor_client):
        response = supervisor_client.delete("/api/equipment/GHOST-999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_equipment_with_active_orders_returns_409(self, supervisor_client, equipment_payload):
        from apps.equipment.models import Equipment
        from apps.work_orders.models import WorkOrder
        from django.utils import timezone
        supervisor_client.post("/api/equipment/", equipment_payload, format="json")
        eq = Equipment.objects.get(id_unico="EQ-CTRL-001")
        from apps.users.models import User
        sup = User.objects.create_user(
            username="eq_del_sup2", password="pass", nombre_completo="S", rol="SUPERVISOR"
        )
        WorkOrder.objects.create(
            tipo="CORRECTIVO", estado="EN_PROCESO", descripcion="Activa",
            fecha_inicio=timezone.now(), fk_equipo=eq, fk_tecnico=sup,
        )
        response = supervisor_client.delete("/api/equipment/EQ-CTRL-001/")
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_list_with_search_filter(self, supervisor_client, equipment_payload):
        supervisor_client.post("/api/equipment/", equipment_payload, format="json")
        response = supervisor_client.get("/api/equipment/?search=Bomba")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_tecnico_cannot_delete_equipment(self, tecnico_client, supervisor_client, equipment_payload):
        supervisor_client.post("/api/equipment/", equipment_payload, format="json")
        response = tecnico_client.delete("/api/equipment/EQ-CTRL-001/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
