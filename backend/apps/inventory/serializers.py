"""DRF serializers for the inventory app."""

from rest_framework import serializers

from apps.inventory.models import SparePart


class SparePartReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SparePart
        fields = [
            "id_repuesto",
            "nombre",
            "codigo",
            "descripcion",
            "cantidad_stock",
            "unidad_medida",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class SparePartCreateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=200)
    codigo = serializers.CharField(max_length=100)
    descripcion = serializers.CharField(required=False, allow_blank=True, default="")
    cantidad_stock = serializers.IntegerField(min_value=0, default=0)
    unidad_medida = serializers.CharField(max_length=50, default="unidades")


class SparePartUpdateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=200, required=False)
    descripcion = serializers.CharField(allow_blank=True, required=False)
    cantidad_stock = serializers.IntegerField(min_value=0, required=False)
    unidad_medida = serializers.CharField(max_length=50, required=False)
