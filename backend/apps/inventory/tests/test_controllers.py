"""Controller tests for inventory app."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture
def supervisor(db):
    return User.objects.create_user(
        username="inv_ctrl_sup",
        password="pass",
        nombre_completo="Supervisor",
        rol="SUPERVISOR",
    )


@pytest.fixture
def tecnico(db):
    return User.objects.create_user(
        username="inv_ctrl_tec",
        password="pass",
        nombre_completo="Tecnico",
        rol="TECNICO",
    )


@pytest.fixture
def supervisor_client(supervisor):
    client = APIClient()
    client.force_authenticate(user=supervisor)
    return client


@pytest.fixture
def tecnico_client(tecnico):
    client = APIClient()
    client.force_authenticate(user=tecnico)
    return client


@pytest.mark.django_db
class TestSparePartControllers:
    def test_list_spare_parts_tecnico(self, tecnico_client):
        response = tecnico_client.get("/api/inventory/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_spare_part_supervisor(self, supervisor_client):
        response = supervisor_client.post(
            "/api/inventory/",
            {"nombre": "Correa", "codigo": "CRR-001", "cantidad_stock": 5},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_tecnico_cannot_create_spare_part(self, tecnico_client):
        response = tecnico_client.post(
            "/api/inventory/",
            {"nombre": "Correa", "codigo": "CRR-002", "cantidad_stock": 5},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_with_search_returns_filtered(self, supervisor_client):
        supervisor_client.post(
            "/api/inventory/",
            {"nombre": "Filtro de aire", "codigo": "FLT-AIR-01", "cantidad_stock": 3},
            format="json",
        )
        response = supervisor_client.get("/api/inventory/?search=Filtro")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_list_search_no_results(self, supervisor_client):
        response = supervisor_client.get("/api/inventory/?search=XYZNONEXISTENT")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_create_duplicate_code_returns_409(self, supervisor_client):
        payload = {"nombre": "Rodamiento", "codigo": "ROD-DUP-01", "cantidad_stock": 10}
        supervisor_client.post("/api/inventory/", payload, format="json")
        response = supervisor_client.post("/api/inventory/", payload, format="json")
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_get_detail_success(self, supervisor_client):
        res = supervisor_client.post(
            "/api/inventory/",
            {"nombre": "Tornillo", "codigo": "TRN-DETAIL-01", "cantidad_stock": 20},
            format="json",
        )
        part_id = res.data["id_repuesto"]
        response = supervisor_client.get(f"/api/inventory/{part_id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["codigo"] == "TRN-DETAIL-01"

    def test_get_detail_not_found(self, supervisor_client):
        response = supervisor_client.get("/api/inventory/999999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_spare_part_success(self, supervisor_client):
        res = supervisor_client.post(
            "/api/inventory/",
            {"nombre": "Aceite", "codigo": "ACE-PATCH-01", "cantidad_stock": 5},
            format="json",
        )
        part_id = res.data["id_repuesto"]
        response = supervisor_client.patch(
            f"/api/inventory/{part_id}/",
            {"cantidad_stock": 15},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["cantidad_stock"] == 15

    def test_patch_spare_part_not_found(self, supervisor_client):
        response = supervisor_client.patch(
            "/api/inventory/999999/",
            {"cantidad_stock": 5},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_tecnico_cannot_patch_spare_part(self, tecnico_client, supervisor_client):
        res = supervisor_client.post(
            "/api/inventory/",
            {"nombre": "Valvula", "codigo": "VLV-PERM-01", "cantidad_stock": 5},
            format="json",
        )
        part_id = res.data["id_repuesto"]
        response = tecnico_client.patch(
            f"/api/inventory/{part_id}/",
            {"cantidad_stock": 1},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
