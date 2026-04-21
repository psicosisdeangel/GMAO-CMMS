"""AuditLog model — append-only (REQ-13).

No UPDATE or DELETE endpoints are exposed.  The repository intentionally
does not provide modification methods.
"""

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Immutable record of every critical system action.

    Retention: ≥ 5 years (REQ-13).  Do NOT delete rows even if the
    referenced entity is removed.
    """

    id_log = models.AutoField(primary_key=True)
    action = models.CharField(max_length=100)
    entity = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="actor_id",
        related_name="audit_logs",
    )
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        indexes = [
            models.Index(fields=["timestamp", "entity"], name="idx_audit_ts_entity"),
        ]
        # Application-level immutability: no update/delete methods in repo
        verbose_name = "registro de auditoría"
        verbose_name_plural = "registros de auditoría"

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.action} on {self.entity}#{self.entity_id}"
