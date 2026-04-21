"""Inventory models — spare parts management (REQ-04, REQ-12)."""

from django.db import models


class SparePart(models.Model):
    """A spare part that can be used when closing a corrective work order."""

    id_repuesto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    cantidad_stock = models.PositiveIntegerField(default=0)
    unidad_medida = models.CharField(max_length=50, default="unidades")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "spare_parts"
        verbose_name = "repuesto"
        verbose_name_plural = "repuestos"

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nombre} (stock: {self.cantidad_stock})"
