"""Read-only serializer for AuditLog."""

from rest_framework import serializers

from apps.audit.models import AuditLog


class AuditLogReadSerializer(serializers.ModelSerializer):
    actor_username = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id_log",
            "action",
            "entity",
            "entity_id",
            "actor",
            "actor_username",
            "details",
            "timestamp",
        ]
        read_only_fields = fields

    def get_actor_username(self, obj: AuditLog) -> str | None:
        return obj.actor.username if obj.actor else None
