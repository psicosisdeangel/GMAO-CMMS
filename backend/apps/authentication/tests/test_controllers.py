"""Tests for authentication endpoints.

EQ-01: checks 403 on role-restricted resources.
EQ-02: expired/invalid token → 401.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def active_user(db):
    return User.objects.create_user(
        username="auth_user",
        password="TestPass123",
        nombre_completo="Auth User",
        rol=User.Rol.TECNICO,
    )


@pytest.mark.django_db
class TestLoginController:
    def test_valid_credentials_return_tokens(self, api_client, active_user):
        response = api_client.post(
            "/api/auth/login/",
            {"username": "auth_user", "password": "TestPass123"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["rol"] == "TECNICO"

    def test_invalid_password_returns_401(self, api_client, active_user):
        response = api_client.post(
            "/api/auth/login/",
            {"username": "auth_user", "password": "WrongPassword"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_inactive_user_returns_401(self, api_client, db):
        user = User.objects.create_user(
            username="inactive_user",
            password="TestPass123",
            nombre_completo="Inactive",
            rol=User.Rol.TECNICO,
        )
        user.is_active = False
        user.save()
        response = api_client.post(
            "/api/auth/login/",
            {"username": "inactive_user", "password": "TestPass123"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_fields_returns_400(self, api_client):
        response = api_client.post("/api/auth/login/", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthenticated_request_to_protected_endpoint_returns_401(self, api_client):
        """EQ-02: no token → 401."""
        response = api_client.get("/api/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRegisterController:
    def test_register_creates_tecnico(self, api_client):
        response = api_client.post(
            "/api/auth/register/",
            {"username": "new_reg_user", "password": "SecurePass123",
             "nombre_completo": "Nuevo Técnico"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert response.data["user"]["rol"] == "TECNICO"

    def test_register_duplicate_username_returns_409(self, api_client, active_user):
        response = api_client.post(
            "/api/auth/register/",
            {"username": active_user.username, "password": "SecurePass123",
             "nombre_completo": "Duplicado"},
            format="json",
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_register_missing_fields_returns_400(self, api_client):
        response = api_client.post("/api/auth/register/", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTokenRefresh:
    def test_refresh_with_valid_token(self, api_client, active_user):
        login = api_client.post(
            "/api/auth/login/",
            {"username": "auth_user", "password": "TestPass123"},
            format="json",
        )
        refresh_token = login.data["refresh"]
        response = api_client.post(
            "/api/auth/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_refresh_with_invalid_token_returns_401(self, api_client):
        response = api_client.post(
            "/api/auth/refresh/",
            {"refresh": "invalid.token.here"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
