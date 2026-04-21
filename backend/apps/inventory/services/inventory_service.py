"""Business logic for the inventory app."""

from django.db import transaction

from apps.inventory.exceptions import (
    DuplicateSparePartCodeError,
    InsufficientStockError,
    SparePartNotFoundError,
)
from apps.inventory.models import SparePart
from apps.inventory.repositories.inventory_repository import InventoryRepository


class InventoryService:
    @staticmethod
    @transaction.atomic
    def create_spare_part(data: dict, actor) -> SparePart:
        """Create a new spare part.

        Raises:
            DuplicateSparePartCodeError: If the code already exists.
        """
        from apps.audit.services.audit_service import AuditService

        if InventoryRepository.exists_by_codigo(data["codigo"]):
            raise DuplicateSparePartCodeError(f"Código '{data['codigo']}' ya existe.")
        spare_part = InventoryRepository.create(data)
        AuditService.log(
            action="CREATE_SPARE_PART",
            entity="SparePart",
            entity_id=str(spare_part.id_repuesto),
            actor=actor,
            details={"codigo": spare_part.codigo},
        )
        return spare_part

    @staticmethod
    @transaction.atomic
    def update_spare_part(id_repuesto: int, data: dict, actor) -> SparePart:
        """Update a spare part's mutable fields.

        Raises:
            SparePartNotFoundError: If the spare part does not exist.
        """
        spare_part = InventoryRepository.get_by_id(id_repuesto)
        if spare_part is None:
            raise SparePartNotFoundError(f"Repuesto {id_repuesto} no encontrado.")
        updated = InventoryRepository.update(spare_part, data)
        return updated

    @staticmethod
    def get_spare_part(id_repuesto: int) -> SparePart:
        """Fetch a spare part or raise SparePartNotFoundError."""
        sp = InventoryRepository.get_by_id(id_repuesto)
        if sp is None:
            raise SparePartNotFoundError(f"Repuesto {id_repuesto} no encontrado.")
        return sp

    @staticmethod
    def list_spare_parts() -> "list[SparePart]":
        return InventoryRepository.list_all()

    @staticmethod
    def decrement_stock(id_repuesto: int, cantidad: int) -> None:
        """Atomically decrement stock for a spare part.

        Raises:
            SparePartNotFoundError: If the spare part does not exist.
            InsufficientStockError: If there is not enough stock.
        """
        sp = InventoryRepository.get_by_id(id_repuesto)
        if sp is None:
            raise SparePartNotFoundError(f"Repuesto {id_repuesto} no encontrado.")
        updated_rows = InventoryRepository.decrement_stock(id_repuesto, cantidad)
        if updated_rows == 0:
            raise InsufficientStockError(
                f"Stock insuficiente para repuesto {id_repuesto}. "
                f"Disponible: {sp.cantidad_stock}, solicitado: {cantidad}."
            )
