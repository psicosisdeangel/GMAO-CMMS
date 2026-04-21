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
