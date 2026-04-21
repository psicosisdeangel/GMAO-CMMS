"""Tests for AuditService and AuditRepository (REQ-13)."""

import pytest

from apps.audit.models import AuditLog
from apps.audit.repositories.audit_repository import AuditRepository
from apps.audit.services.audit_service import AuditService


@pytest.mark.django_db
class TestAuditRepository:
    def test_create_log_entry(self):
        log = AuditRepository.create(
            action="TEST_ACTION",
            entity="Equipment",
            entity_id="EQ-001",
            actor=None,
            details={"test": True},
        )
        assert log.id_log is not None
        assert log.action == "TEST_ACTION"
        assert log.entity_id == "EQ-001"

    def test_no_update_method(self):
        """AuditRepository must NOT expose update or delete methods."""
        assert not hasattr(AuditRepository, "update")
        assert not hasattr(AuditRepository, "delete")

    def test_list_all_with_entity_filter(self):
        AuditRepository.create("A1", "Equipment", "EQ-001", None)
        AuditRepository.create("A2", "WorkOrder", "WO-001", None)
        eq_logs = AuditRepository.list_all(entity="Equipment")
        for log in eq_logs:
            assert log.entity == "Equipment"


@pytest.mark.django_db
class TestAuditService:
    def test_log_creates_entry(self):
        AuditService.log(
            action="CREATE_EQUIPMENT",
            entity="Equipment",
            entity_id="EQ-TEST",
            actor=None,
        )
        assert AuditLog.objects.filter(
            action="CREATE_EQUIPMENT", entity_id="EQ-TEST"
        ).exists()
