"""Equipment model (REQ-01).

`id_unico` is the business PK — immutable after creation.
"""

from django.db import models


class Equipment(models.Model):
    """An industrial piece of equipment tracked by the GMAO system."""

    id_unico = models.CharField(max_length=50, unique=True, primary_key=True)
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200)
    fecha_instalacion = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=50, default="ACTIVO")
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "equipment"
        indexes = [
            models.Index(fields=["tipo"], name="idx_equipment_tipo"),
            models.Index(fields=["ubicacion"], name="idx_equipment_ubicacion"),
        ]

    def __str__(self) -> str:
        return f"{self.id_unico} — {self.nombre}"
