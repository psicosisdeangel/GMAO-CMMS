"""AuditService — thin facade over AuditRepository (REQ-13)."""

from typing import Optional

from apps.audit.repositories.audit_repository import AuditRepository


class AuditService:
    @staticmethod
    def log(
        action: str,
        entity: str,
        entity_id: str,
        actor,
        details: Optional[dict] = None,
    ) -> None:
        """Record a critical system action in the immutable audit log.

        Args:
            action:    Short action identifier string.
            entity:    Affected model/entity name.
            entity_id: String key of the affected record.
            actor:     The User performing the action (or None for system).
            details:   Optional dict with extra context.
        """
        AuditRepository.create(
            action=action,
            entity=entity,
            entity_id=entity_id,
            actor=actor,
            details=details or {},
        )
