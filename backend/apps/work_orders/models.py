"""Work order models (REQ-02, 03, 04, 05)."""

from django.conf import settings
from django.db import models


class WorkOrder(models.Model):
    """A maintenance work order — preventive or corrective."""

    class Tipo(models.TextChoices):
        PREVENTIVO = "PREVENTIVO", "Preventivo"
        CORRECTIVO = "CORRECTIVO", "Correctivo"

    class Estado(models.TextChoices):
        PROGRAMADO = "PROGRAMADO", "Programado"
        EN_PROCESO = "EN_PROCESO", "En Proceso"
        CERRADA = "CERRADA", "Cerrada"

    class Frecuencia(models.TextChoices):
        UNICA = "UNICA", "Única"
        MENSUAL = "MENSUAL", "Mensual"
        TRIMESTRAL = "TRIMESTRAL", "Trimestral"
        ANUAL = "ANUAL", "Anual"

    id_orden = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PROGRAMADO)
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    frecuencia = models.CharField(
        max_length=20, choices=Frecuencia.choices, default=Frecuencia.UNICA
    )
    fk_equipo = models.ForeignKey(
        "equipment.Equipment",
        on_delete=models.PROTECT,
        related_name="work_orders",
        db_column="fk_equipo",
    )
    fk_tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="work_orders",
        db_column="fk_tecnico",
    )
    notas_cierre = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "work_orders"
        indexes = [
            # REQ-06: history queries ordered by date
            models.Index(fields=["fk_equipo", "-fecha_inicio"], name="idx_wo_equipo_fecha"),
            models.Index(fields=["estado"], name="idx_wo_estado"),
            models.Index(fields=["fk_tecnico"], name="idx_wo_tecnico"),
        ]

    def __str__(self) -> str:
        return f"OT-{self.id_orden} [{self.tipo}] {self.estado}"


class WorkOrderSparePart(models.Model):
    """Join table tracking spare parts consumed in a work order."""

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name="spare_parts_used",
    )
    spare_part = models.ForeignKey(
        "inventory.SparePart",
        on_delete=models.PROTECT,
    )
    cantidad_usada = models.PositiveIntegerField()

    class Meta:
        db_table = "work_order_spare_parts"
        unique_together = ("work_order", "spare_part")
