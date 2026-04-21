"""Audit repository — CREATE ONLY.  No update or delete methods (REQ-13)."""

from typing import Optional

from apps.audit.models import AuditLog


class AuditRepository:
    @staticmethod
    def create(
        action: str,
        entity: str,
        entity_id: str,
        actor,
        details: Optional[dict] = None,
    ) -> AuditLog:
        """Persist a new audit log entry.

        Args:
            action:    Short action identifier (e.g. "CREATE_EQUIPMENT").
            entity:    Model/entity name (e.g. "Equipment").
            entity_id: String representation of the entity PK.
            actor:     The User performing the action, or None for system.
            details:   Arbitrary JSON payload for context.

        Returns:
            The newly created AuditLog instance.
        """
        return AuditLog.objects.create(
            action=action,
            entity=entity,
            entity_id=str(entity_id),
            actor=actor,
            details=details or {},
        )

    @staticmethod
    def list_all(entity: Optional[str] = None, action: Optional[str] = None):
        """Return audit logs queryset, optionally filtered."""
        qs = AuditLog.objects.select_related("actor").order_by("-timestamp")
        if entity:
            qs = qs.filter(entity=entity)
        if action:
            qs = qs.filter(action=action)
        return qs
