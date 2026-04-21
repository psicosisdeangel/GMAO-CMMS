"""DRF serializers for the work_orders app (shape validation only)."""

from rest_framework import serializers

from apps.work_orders.models import WorkOrder, WorkOrderSparePart


class SparePartUsedSerializer(serializers.Serializer):
    """Nested input for spare parts used when closing an order."""

    spare_part_id = serializers.IntegerField()
    cantidad_usada = serializers.IntegerField(min_value=1)


class WorkOrderCreateSerializer(serializers.Serializer):
    """Input shape for creating a work order."""

    tipo = serializers.ChoiceField(choices=WorkOrder.Tipo.choices)
    descripcion = serializers.CharField()
    fecha_inicio = serializers.DateTimeField()
    frecuencia = serializers.ChoiceField(
        choices=WorkOrder.Frecuencia.choices,
        default=WorkOrder.Frecuencia.UNICA,
    )
    fk_equipo_id = serializers.CharField(max_length=50)
    fk_tecnico_id = serializers.IntegerField(required=False, allow_null=True)


class WorkOrderUpdateSerializer(serializers.Serializer):
    """Input shape for partial update (cannot change estado directly)."""

    descripcion = serializers.CharField(required=False)
    fecha_inicio = serializers.DateTimeField(required=False)
    fk_tecnico_id = serializers.IntegerField(required=False, allow_null=True)
    frecuencia = serializers.ChoiceField(
        choices=WorkOrder.Frecuencia.choices, required=False
    )


class WorkOrderCloseSerializer(serializers.Serializer):
    """Input shape for closing a work order."""

    notas_cierre = serializers.CharField(required=False, allow_blank=True, default="")
    spare_parts_used = SparePartUsedSerializer(many=True, required=False, default=list)


class WorkOrderReadSerializer(serializers.ModelSerializer):
    """Full read representation — field names match frontend types."""

    fk_equipo = serializers.CharField(source="fk_equipo_id", read_only=True)
    fk_equipo_nombre = serializers.SerializerMethodField()
    fk_tecnico = serializers.IntegerField(source="fk_tecnico_id", read_only=True, allow_null=True)
    fk_tecnico_nombre = serializers.SerializerMethodField()
    spare_parts_used = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = [
            "id_orden",
            "tipo",
            "estado",
            "descripcion",
            "fecha_inicio",
            "fecha_cierre",
            "frecuencia",
            "fk_equipo",
            "fk_equipo_nombre",
            "fk_tecnico",
            "fk_tecnico_nombre",
            "notas_cierre",
            "spare_parts_used",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_fk_equipo_nombre(self, obj: WorkOrder) -> str:
        return obj.fk_equipo.nombre if obj.fk_equipo_id else ""

    def get_fk_tecnico_nombre(self, obj: WorkOrder) -> str | None:
        return obj.fk_tecnico.nombre_completo if obj.fk_tecnico_id else None

    def get_spare_parts_used(self, obj: WorkOrder) -> list:
        return [
            {
                "spare_part_id": sp.spare_part_id,
                "spare_part_nombre": sp.spare_part.nombre,
                "cantidad_usada": sp.cantidad_usada,
            }
            for sp in obj.spare_parts_used.select_related("spare_part").all()
        ]
