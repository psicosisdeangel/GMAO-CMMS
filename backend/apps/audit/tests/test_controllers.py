"""Controller tests for audit logs (REQ-13)."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.audit.repositories.audit_repository import AuditRepository
from apps.users.models import User


@pytest.fixture
def supervisor(db):
    return User.objects.create_user(
        username="aud_ctrl_sup",
        password="pass",
        nombre_completo="Supervisor",
        rol="SUPERVISOR",
    )


@pytest.fixture
def tecnico(db):
    return User.objects.create_user(
        username="aud_ctrl_tec",
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


@pytest.mark.django_db
class TestAuditLogController:
    def test_supervisor_can_list_audit_logs(self, supervisor_client):
        AuditRepository.create("CREATE_EQUIPMENT", "Equipment", "EQ-001", None)
        response = supervisor_client.get("/api/audit/")
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_tecnico_cannot_access_audit(self, tecnico_client):
        response = tecnico_client.get("/api/audit/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_access_audit(self):
        client = APIClient()
        response = client.get("/api/audit/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_filter_by_entity(self, supervisor_client):
        AuditRepository.create("CREATE_EQUIPMENT", "Equipment", "EQ-AUD-01", None)
        AuditRepository.create("CLOSE_WORK_ORDER", "WorkOrder", "WO-AUD-01", None)
        response = supervisor_client.get("/api/audit/?entity=Equipment")
        assert response.status_code == status.HTTP_200_OK
        for log in response.data["results"]:
            assert log["entity"] == "Equipment"

    def test_filter_by_action(self, supervisor_client):
        AuditRepository.create("CREATE_EQUIPMENT", "Equipment", "EQ-AUD-02", None)
        response = supervisor_client.get("/api/audit/?action=CREATE_EQUIPMENT")
        assert response.status_code == status.HTTP_200_OK
        for log in response.data["results"]:
            assert log["action"] == "CREATE_EQUIPMENT"

    def test_empty_result_with_unknown_entity(self, supervisor_client):
        response = supervisor_client.get("/api/audit/?entity=NONEXISTENT")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
