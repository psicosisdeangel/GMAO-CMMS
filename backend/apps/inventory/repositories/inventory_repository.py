"""Repository for SparePart — all ORM access."""

from typing import Optional

from django.db.models import F, Q

from apps.inventory.models import SparePart


class InventoryRepository:
    @staticmethod
    def get_by_id(id_repuesto: int) -> Optional[SparePart]:
        return SparePart.objects.filter(id_repuesto=id_repuesto).first()

    @staticmethod
    def get_by_codigo(codigo: str) -> Optional[SparePart]:
        return SparePart.objects.filter(codigo=codigo).first()

    @staticmethod
    def list_all(search: Optional[str] = None) -> "list[SparePart]":
        qs = SparePart.objects.all().order_by("nombre")
        if search:
            qs = qs.filter(Q(nombre__icontains=search) | Q(codigo__icontains=search))
        return list(qs)

    @staticmethod
    def create(data: dict) -> SparePart:
        return SparePart.objects.create(**data)

    @staticmethod
    def update(spare_part: SparePart, data: dict) -> SparePart:
        for field, value in data.items():
            setattr(spare_part, field, value)
        spare_part.save()
        return spare_part

    @staticmethod
    def decrement_stock(id_repuesto: int, cantidad: int) -> int:
        """Atomically decrement stock.  Returns the number of rows updated."""
        return SparePart.objects.filter(
            id_repuesto=id_repuesto,
            cantidad_stock__gte=cantidad,
        ).update(cantidad_stock=F("cantidad_stock") - cantidad)

    @staticmethod
    def exists_by_codigo(codigo: str) -> bool:
        return SparePart.objects.filter(codigo=codigo).exists()
