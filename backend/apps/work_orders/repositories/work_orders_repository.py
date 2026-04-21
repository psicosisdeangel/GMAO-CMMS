"""Repository for WorkOrder and WorkOrderSparePart — all ORM access."""

from typing import Optional

from apps.work_orders.models import WorkOrder, WorkOrderSparePart


class WorkOrdersRepository:
    @staticmethod
    def create(data: dict) -> WorkOrder:
        return WorkOrder.objects.create(**data)

    @staticmethod
    def get_by_id(id_orden: int) -> Optional[WorkOrder]:
        return (
            WorkOrder.objects.select_related("fk_equipo", "fk_tecnico")
            .filter(id_orden=id_orden)
            .first()
        )

    @staticmethod
    def list_all(
        tecnico_id: Optional[int] = None,
        estado: Optional[str] = None,
        tipo: Optional[str] = None,
        equipo_id: Optional[str] = None,
    ):
        qs = WorkOrder.objects.select_related("fk_equipo", "fk_tecnico").order_by("-fecha_inicio")
        if tecnico_id is not None:
            qs = qs.filter(fk_tecnico_id=tecnico_id)
        if estado:
            qs = qs.filter(estado=estado)
        if tipo:
            qs = qs.filter(tipo=tipo)
        if equipo_id:
            qs = qs.filter(fk_equipo_id=equipo_id)
        return qs

    @staticmethod
    def update(work_order: WorkOrder, data: dict) -> WorkOrder:
        for field, value in data.items():
            setattr(work_order, field, value)
        work_order.save()
        return work_order

    @staticmethod
    def add_spare_part(
        work_order: WorkOrder, spare_part_id: int, cantidad_usada: int
    ) -> WorkOrderSparePart:
        return WorkOrderSparePart.objects.create(
            work_order=work_order,
            spare_part_id=spare_part_id,
            cantidad_usada=cantidad_usada,
        )

    @staticmethod
    def get_equipment_history(equipo_id: str) -> "list[WorkOrder]":
        """Return all orders for an equipment, newest first (REQ-06)."""
        return list(
            WorkOrder.objects.select_related("fk_tecnico")
            .filter(fk_equipo_id=equipo_id)
            .order_by("-fecha_inicio")
        )
