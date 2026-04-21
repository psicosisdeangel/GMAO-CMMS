"""DRF serializers for the equipment app (shape validation only)."""

from rest_framework import serializers

from apps.equipment.models import Equipment


class EquipmentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = [
            "id_unico",
            "nombre",
            "tipo",
            "ubicacion",
            "fecha_instalacion",
            "estado",
            "descripcion",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class EquipmentCreateSerializer(serializers.Serializer):
    """Input shape for creating equipment.  id_unico is required."""

    id_unico = serializers.CharField(max_length=50)
    nombre = serializers.CharField(max_length=200)
    tipo = serializers.CharField(max_length=100)
    ubicacion = serializers.CharField(max_length=200)
    fecha_instalacion = serializers.DateField(required=False, allow_null=True)
    descripcion = serializers.CharField(required=False, allow_blank=True, default="")


class EquipmentUpdateSerializer(serializers.Serializer):
    """Input shape for updating equipment.  id_unico is NOT accepted (REQ-01)."""

    nombre = serializers.CharField(max_length=200, required=False)
    tipo = serializers.CharField(max_length=100, required=False)
    ubicacion = serializers.CharField(max_length=200, required=False)
    estado = serializers.CharField(max_length=50, required=False)
    descripcion = serializers.CharField(allow_blank=True, required=False)
    fecha_instalacion = serializers.DateField(required=False, allow_null=True)
