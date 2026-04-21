"""Controller-level tests for the users app.

Uses DRF's APIClient; mocks the service layer.
Scenario EQ-01: TECNICO attempts SUPERVISOR-only endpoint → 403.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def supervisor_user(db):
    return User.objects.create_user(
        username="supervisor_ctrl",
        password="TestPass123",
        nombre_completo="Supervisor",
        rol=User.Rol.SUPERVISOR,
    )


@pytest.fixture
def tecnico_user(db):
    return User.objects.create_user(
        username="tecnico_ctrl",
        password="TestPass123",
        nombre_completo="Tecnico",
        rol=User.Rol.TECNICO,
    )


@pytest.fixture
def supervisor_client(api_client, supervisor_user):
    api_client.force_authenticate(user=supervisor_user)
    return api_client


@pytest.fixture
def tecnico_client(api_client, tecnico_user):
    api_client.force_authenticate(user=tecnico_user)
    return api_client


@pytest.mark.django_db
class TestUserListCreateController:
    def test_supervisor_can_list_users(self, supervisor_client):
        response = supervisor_client.get("/api/users/")
        assert response.status_code == status.HTTP_200_OK

    def test_tecnico_cannot_list_users(self, tecnico_client):
        """EQ-01: TECNICO → restricted endpoint → 403."""
        response = tecnico_client.get("/api/users/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_list_users(self, api_client):
        response = api_client.get("/api/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_supervisor_can_create_user(self, supervisor_client):
        payload = {
            "username": "new_tech",
            "password": "SecurePass123",
            "email": "new@plant.com",
            "nombre_completo": "New Tech",
            "rol": "TECNICO",
        }
        response = supervisor_client.post("/api/users/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["username"] == "new_tech"

    def test_duplicate_username_returns_409(self, supervisor_client, supervisor_user):
        payload = {
            "username": supervisor_user.username,
            "password": "SecurePass123",
            "email": "",
            "nombre_completo": "Dup",
            "rol": "TECNICO",
        }
        response = supervisor_client.post("/api/users/", payload, format="json")
        assert response.status_code == status.HTTP_409_CONFLICT
