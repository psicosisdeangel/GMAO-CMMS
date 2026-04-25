"""Business logic for work orders (REQ-02, 03, 04, 05, 06, 12)."""

from datetime import timedelta
from typing import Optional

from django.db import transaction
from django.utils import timezone

from apps.work_orders.exceptions import (
    InsufficientStockError,
    WorkOrderClosedError,
    WorkOrderInvalidDateError,
    WorkOrderInvalidTransitionError,
    WorkOrderNotFoundError,
)
from apps.work_orders.models import WorkOrder
from apps.work_orders.repositories.work_orders_repository import WorkOrdersRepository


class WorkOrdersService:
    # ────────────────────────────────────────── CREATE ────────────────────────
    @staticmethod
    @transaction.atomic
    def create_work_order(data: dict, actor) -> WorkOrder:
        """Create a new work order.

        Business rules:
        - REQ-02: fecha_inicio must be >= now (for PREVENTIVO).
        - PREVENTIVO can only be created by SUPERVISOR.
        - Correctivo starts in EN_PROCESO and is assigned to the requesting technician.

        Args:
            data:  Validated payload from WorkOrderCreateSerializer.
            actor: The user creating the order.

        Raises:
            WorkOrderInvalidDateError: If fecha_inicio is in the past (PREVENTIVO).
        """
        from apps.audit.services.audit_service import AuditService

        tipo = data["tipo"]
        fecha_inicio = data["fecha_inicio"]

        # REQ-02: Preventive orders must not have a past date
        if tipo == WorkOrder.Tipo.PREVENTIVO and fecha_inicio < timezone.now():
            raise WorkOrderInvalidDateError(
                "La fecha de inicio de un mantenimiento preventivo no puede ser en el pasado."
            )

        if tipo == WorkOrder.Tipo.PREVENTIVO:
            data["estado"] = WorkOrder.Estado.PROGRAMADO

        # REQ-04: Corrective order → starts EN_PROCESO, assigned to actor (if TECNICO)
        if tipo == WorkOrder.Tipo.CORRECTIVO:
            data["estado"] = WorkOrder.Estado.EN_PROCESO
            if not data.get("fk_tecnico_id"):
                data["fk_tecnico_id"] = actor.id

        order = WorkOrdersRepository.create(data)

        AuditService.log(
            action="CREATE_WORK_ORDER",
            entity="WorkOrder",
            entity_id=str(order.id_orden),
            actor=actor,
            details={"tipo": order.tipo, "equipo": str(order.fk_equipo_id)},
        )
        return order

    # ────────────────────────────────────────── UPDATE ────────────────────────
    @staticmethod
    @transaction.atomic
    def update_work_order(id_orden: int, data: dict, actor) -> WorkOrder:
        """Update mutable fields of a work order.

        Raises:
            WorkOrderNotFoundError: If order does not exist.
            WorkOrderClosedError:   If order is CERRADA (REQ-05 → HTTP 422).
        """
        from apps.audit.services.audit_service import AuditService

        order = WorkOrdersRepository.get_by_id(id_orden)
        if order is None:
            raise WorkOrderNotFoundError(f"Orden {id_orden} no encontrada.")

        # REQ-05: Immutability of closed orders — checked BEFORE any repository call
        if order.estado == WorkOrder.Estado.CERRADA:
            AuditService.log(
                action="DENIED_UPDATE_CLOSED_ORDER",
                entity="WorkOrder",
                entity_id=str(id_orden),
                actor=actor,
                details={"reason": "Orden cerrada", "attempted_data": data},
            )
            raise WorkOrderClosedError(
                f"La orden {id_orden} está cerrada y no puede modificarse."
            )

        updated = WorkOrdersRepository.update(order, data)
        AuditService.log(
            action="UPDATE_WORK_ORDER",
            entity="WorkOrder",
            entity_id=str(id_orden),
            actor=actor,
            details=data,
        )
        return updated

    # ────────────────────────────────────────── START ─────────────────────────
    @staticmethod
    @transaction.atomic
    def start_work_order(id_orden: int, actor) -> WorkOrder:
        """Transition PROGRAMADO → EN_PROCESO.

        Raises:
            WorkOrderNotFoundError:           If order does not exist.
            WorkOrderClosedError:             If already CERRADA.
            WorkOrderInvalidTransitionError:  If not PROGRAMADO.
        """
        order = WorkOrdersRepository.get_by_id(id_orden)
        if order is None:
            raise WorkOrderNotFoundError(f"Orden {id_orden} no encontrada.")
        if order.estado == WorkOrder.Estado.CERRADA:
            raise WorkOrderClosedError(f"La orden {id_orden} está cerrada.")
        if order.estado != WorkOrder.Estado.PROGRAMADO:
            raise WorkOrderInvalidTransitionError(
                f"La orden {id_orden} ya está en estado {order.estado}."
            )

        update_data: dict = {"estado": WorkOrder.Estado.EN_PROCESO}
        if not order.fk_tecnico_id:
            update_data["fk_tecnico_id"] = actor.id
        return WorkOrdersRepository.update(order, update_data)

    # ────────────────────────────────────────── CLOSE ─────────────────────────
    @staticmethod
    @transaction.atomic
    def close_work_order(id_orden: int, data: dict, actor) -> WorkOrder:
        """Close a work order.

        Business rules:
        - REQ-05: Already CERRADA → HTTP 422 + audit.
        - REQ-04/REQ-12: Atomically decrement stock for each spare part used.
        - REQ-03: If PREVENTIVO + frecuencia != UNICA → generate next order.

        Args:
            id_orden: PK of the work order to close.
            data:     Validated payload from WorkOrderCloseSerializer.
            actor:    The user closing the order.

        Raises:
            WorkOrderNotFoundError:  If order does not exist.
            WorkOrderClosedError:    If already CERRADA (HTTP 422).
            InsufficientStockError:  If a spare part has insufficient stock.
        """
        from apps.audit.services.audit_service import AuditService
        from apps.inventory.services.inventory_service import InventoryService

        order = WorkOrdersRepository.get_by_id(id_orden)
        if order is None:
            raise WorkOrderNotFoundError(f"Orden {id_orden} no encontrada.")

        # REQ-05: Check BEFORE touching anything
        if order.estado == WorkOrder.Estado.CERRADA:
            AuditService.log(
                action="DENIED_CLOSE_CLOSED_ORDER",
                entity="WorkOrder",
                entity_id=str(id_orden),
                actor=actor,
                details={"reason": "Ya estaba cerrada"},
            )
            raise WorkOrderClosedError(
                f"La orden {id_orden} ya está cerrada y no puede modificarse."
            )

        # REQ-04/REQ-12: Decrement stock atomically (inside same @transaction.atomic)
        spare_parts_used = data.get("spare_parts_used", [])
        for item in spare_parts_used:
            InventoryService.decrement_stock(
                id_repuesto=item["spare_part_id"],
                cantidad=item["cantidad_usada"],
            )
            WorkOrdersRepository.add_spare_part(
                work_order=order,
                spare_part_id=item["spare_part_id"],
                cantidad_usada=item["cantidad_usada"],
            )

        # Close the order
        now = timezone.now()
        closed_order = WorkOrdersRepository.update(
            order,
            {
                "estado": WorkOrder.Estado.CERRADA,
                "fecha_cierre": now,
                "notas_cierre": data.get("notas_cierre", ""),
            },
        )

        AuditService.log(
            action="CLOSE_WORK_ORDER",
            entity="WorkOrder",
            entity_id=str(id_orden),
            actor=actor,
            details={"notas_cierre": closed_order.notas_cierre},
        )

        # REQ-03: Generate next recurring order for PREVENTIVO
        if (
            closed_order.tipo == WorkOrder.Tipo.PREVENTIVO
            and closed_order.frecuencia != WorkOrder.Frecuencia.UNICA
        ):
            WorkOrdersService._generate_next_recurring_order(closed_order, actor)

        return closed_order

    # ──────────────────────────────── RECURRING GENERATION (REQ-03) ──────────
    @staticmethod
    def _generate_next_recurring_order(closed_order: WorkOrder, actor) -> WorkOrder:
        """Generate the next recurring preventive work order (REQ-03).

        The new order starts PROGRAMADO with no assigned technician.
        """
        from apps.audit.services.audit_service import AuditService

        interval_map = {
            WorkOrder.Frecuencia.MENSUAL: timedelta(days=30),
            WorkOrder.Frecuencia.TRIMESTRAL: timedelta(days=90),
            WorkOrder.Frecuencia.ANUAL: timedelta(days=365),
        }
        interval = interval_map[closed_order.frecuencia]
        next_fecha = closed_order.fecha_cierre + interval

        next_order = WorkOrdersRepository.create(
            {
                "tipo": WorkOrder.Tipo.PREVENTIVO,
                "estado": WorkOrder.Estado.PROGRAMADO,
                "descripcion": closed_order.descripcion,
                "fecha_inicio": next_fecha,
                "frecuencia": closed_order.frecuencia,
                "fk_equipo_id": closed_order.fk_equipo_id,
                "fk_tecnico_id": None,  # Supervisor must assign
            }
        )

        AuditService.log(
            action="AUTO_GENERATED_RECURRING_ORDER",
            entity="WorkOrder",
            entity_id=str(next_order.id_orden),
            actor=actor,
            details={
                "origin_order": closed_order.id_orden,
                "frecuencia": closed_order.frecuencia,
            },
        )
        return next_order

    # ────────────────────────────────────────── READ ──────────────────────────
    @staticmethod
    def get_work_order(id_orden: int) -> WorkOrder:
        """Fetch a work order or raise WorkOrderNotFoundError."""
        order = WorkOrdersRepository.get_by_id(id_orden)
        if order is None:
            raise WorkOrderNotFoundError(f"Orden {id_orden} no encontrada.")
        return order

    @staticmethod
    def list_work_orders(
        actor,
        estado: Optional[str] = None,
        tipo: Optional[str] = None,
        equipo_id: Optional[str] = None,
    ) -> "list[WorkOrder]":
        """Return work orders filtered by role.

        - TECNICO sees only their own orders.
        - SUPERVISOR sees all orders.
        """
        tecnico_id = actor.id if actor.rol == "TECNICO" else None
        return WorkOrdersRepository.list_all(
            tecnico_id=tecnico_id,
            estado=estado,
            tipo=tipo,
            equipo_id=equipo_id,
        )

    @staticmethod
    def get_equipment_history(equipo_id: str) -> "list[WorkOrder]":
        """Return full maintenance history for an equipment (REQ-06)."""
        return WorkOrdersRepository.get_equipment_history(equipo_id)
