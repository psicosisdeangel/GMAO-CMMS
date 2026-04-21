"""Repository for Equipment — all ORM access."""

from typing import Optional

from apps.equipment.models import Equipment


class EquipmentRepository:
    @staticmethod
    def exists_by_id_unico(id_unico: str) -> bool:
        return Equipment.objects.filter(id_unico=id_unico).exists()

    @staticmethod
    def create(data: dict) -> Equipment:
        return Equipment.objects.create(**data)

    @staticmethod
    def get_by_id(id_unico: str) -> Optional[Equipment]:
        return Equipment.objects.filter(id_unico=id_unico).first()

    @staticmethod
    def list_all(tipo: Optional[str] = None, ubicacion: Optional[str] = None, search: Optional[str] = None) -> "QuerySet":
        from django.db.models import QuerySet
        qs = Equipment.objects.all().order_by("id_unico")
        if tipo:
            qs = qs.filter(tipo__icontains=tipo)
        if ubicacion:
            qs = qs.filter(ubicacion__icontains=ubicacion)
        if search:
            qs = qs.filter(nombre__icontains=search) | qs.filter(id_unico__icontains=search) | qs.filter(tipo__icontains=search)
        return qs

    @staticmethod
    def update(equipment: Equipment, data: dict) -> Equipment:
        for field, value in data.items():
            setattr(equipment, field, value)
        equipment.save()
        return equipment

    @staticmethod
    def delete(equipment: Equipment) -> None:
        equipment.delete()

    @staticmethod
    def has_active_work_orders(id_unico: str) -> bool:
        """Return True if there are open work orders for this equipment."""
        return Equipment.objects.filter(
            id_unico=id_unico,
            work_orders__estado__in=["PROGRAMADO", "EN_PROCESO"],
        ).exists()
