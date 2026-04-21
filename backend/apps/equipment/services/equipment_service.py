"""Business logic for the equipment app (REQ-01)."""

from django.db import transaction

from apps.equipment.exceptions import (
    DuplicateEquipmentIdError,
    EquipmentHasActiveOrdersError,
    EquipmentIdImmutableError,
    EquipmentNotFoundError,
)
from apps.equipment.models import Equipment
from apps.equipment.repositories.equipment_repository import EquipmentRepository


class EquipmentService:
    @staticmethod
    @transaction.atomic
    def create_equipment(data: dict, actor) -> Equipment:
        """Create a new equipment record.

        Args:
            data:  Validated payload from EquipmentCreateSerializer.
            actor: The supervisor performing the action.

        Raises:
            DuplicateEquipmentIdError: If id_unico already exists.
        """
        from apps.audit.services.audit_service import AuditService

        if EquipmentRepository.exists_by_id_unico(data["id_unico"]):
            raise DuplicateEquipmentIdError(f"ID '{data['id_unico']}' ya existe.")

        equipment = EquipmentRepository.create(data)

        AuditService.log(
            action="CREATE_EQUIPMENT",
            entity="Equipment",
            entity_id=equipment.id_unico,
            actor=actor,
            details={"nombre": equipment.nombre, "tipo": equipment.tipo},
        )
        return equipment

    @staticmethod
    @transaction.atomic
    def update_equipment(id_unico: str, data: dict, actor) -> Equipment:
        """Update mutable fields of an equipment record.

        Raises:
            EquipmentNotFoundError:  If id_unico does not exist.
            EquipmentIdImmutableError: If the payload contains 'id_unico' (REQ-01).
        """
        from apps.audit.services.audit_service import AuditService

        # REQ-01: id_unico cannot be changed — enforce in service as last line of defence
        if "id_unico" in data:
            raise EquipmentIdImmutableError("El campo 'id_unico' es inmutable y no puede cambiarse.")

        equipment = EquipmentRepository.get_by_id(id_unico)
        if equipment is None:
            raise EquipmentNotFoundError(f"Equipo '{id_unico}' no encontrado.")

        updated = EquipmentRepository.update(equipment, data)

        AuditService.log(
            action="UPDATE_EQUIPMENT",
            entity="Equipment",
            entity_id=id_unico,
            actor=actor,
            details=data,
        )
        return updated

    @staticmethod
    @transaction.atomic
    def delete_equipment(id_unico: str, actor) -> None:
        """Delete an equipment record.

        Raises:
            EquipmentNotFoundError:         If id_unico does not exist.
            EquipmentHasActiveOrdersError:  If active work orders exist.
        """
        from apps.audit.services.audit_service import AuditService

        equipment = EquipmentRepository.get_by_id(id_unico)
        if equipment is None:
            raise EquipmentNotFoundError(f"Equipo '{id_unico}' no encontrado.")

        if EquipmentRepository.has_active_work_orders(id_unico):
            raise EquipmentHasActiveOrdersError(
                f"El equipo '{id_unico}' tiene órdenes de trabajo activas."
            )

        EquipmentRepository.delete(equipment)

        AuditService.log(
            action="DELETE_EQUIPMENT",
            entity="Equipment",
            entity_id=id_unico,
            actor=actor,
        )

    @staticmethod
    def get_equipment(id_unico: str) -> Equipment:
        """Fetch equipment or raise EquipmentNotFoundError."""
        equipment = EquipmentRepository.get_by_id(id_unico)
        if equipment is None:
            raise EquipmentNotFoundError(f"Equipo '{id_unico}' no encontrado.")
        return equipment

    @staticmethod
    def list_equipment(tipo: str | None = None, ubicacion: str | None = None, search: str | None = None):
        """Return a filtered queryset of equipment."""
        return EquipmentRepository.list_all(tipo=tipo, ubicacion=ubicacion, search=search)
