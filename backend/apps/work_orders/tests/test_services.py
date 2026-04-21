"""Unit tests for WorkOrdersService.

Key scenarios:
- REQ-02: fecha_inicio in past for PREVENTIVO → error
- REQ-04: Corrective order → EN_PROCESO, assigned to actor
- REQ-05 (EQ-04): PATCH on CERRADA → WorkOrderClosedError
- EQ-03: Multi-table failure → rollback (tested via insufficient stock)
- REQ-03: Recurring order generated on close
"""

import pytest
from django.utils import timezone

from apps.equipment.models import Equipment
from apps.inventory.models import SparePart
from apps.users.models import User
from apps.work_orders.exceptions import WorkOrderClosedError, WorkOrderInvalidDateError
from apps.work_orders.models import WorkOrder
from apps.work_orders.services.work_orders_service import WorkOrdersService


@pytest.fixture
def supervisor(db):
    return User.objects.create_user(
        username="wo_supervisor",
        password="pass",
        nombre_completo="Supervisor",
        rol="SUPERVISOR",
    )


@pytest.fixture
def tecnico(db):
    return User.objects.create_user(
        username="wo_tecnico",
        password="pass",
        nombre_completo="Tecnico",
        rol="TECNICO",
    )


@pytest.fixture
def equipment(db):
    return Equipment.objects.create(
        id_unico="EQ-WO-001",
        nombre="Motor Test",
        tipo="Motor",
        ubicacion="Zona A",
    )


@pytest.fixture
def spare_part(db):
    return SparePart.objects.create(nombre="Correa", codigo="CRR-WO", cantidad_stock=5)


@pytest.fixture
def future_date():
    return timezone.now() + timezone.timedelta(days=7)


@pytest.mark.django_db
class TestCreateWorkOrder:
    def test_create_preventivo_future_date(self, supervisor, equipment, future_date):
        order = WorkOrdersService.create_work_order(
            data={
                "tipo": "PREVENTIVO",
                "descripcion": "Mantenimiento mensual",
                "fecha_inicio": future_date,
                "frecuencia": "MENSUAL",
                "fk_equipo_id": equipment.id_unico,
            },
            actor=supervisor,
        )
        assert order.tipo == "PREVENTIVO"
        assert order.estado == "PROGRAMADO"

    def test_create_preventivo_past_date_raises(self, supervisor, equipment):
        """REQ-02: past fecha_inicio for PREVENTIVO → error."""
        past = timezone.now() - timezone.timedelta(days=1)
        with pytest.raises(WorkOrderInvalidDateError):
            WorkOrdersService.create_work_order(
                data={
                    "tipo": "PREVENTIVO",
                    "descripcion": "Test",
                    "fecha_inicio": past,
                    "fk_equipo_id": equipment.id_unico,
                },
                actor=supervisor,
            )

    def test_create_correctivo_assigned_to_actor(self, tecnico, equipment):
        """REQ-04: correctivo starts EN_PROCESO, assigned to requesting technician."""
        order = WorkOrdersService.create_work_order(
            data={
                "tipo": "CORRECTIVO",
                "descripcion": "Falla en motor",
                "fecha_inicio": timezone.now(),
                "fk_equipo_id": equipment.id_unico,
            },
            actor=tecnico,
        )
        assert order.estado == "EN_PROCESO"
        assert order.fk_tecnico_id == tecnico.id


@pytest.mark.django_db
class TestCloseWorkOrder:
    def test_close_already_closed_raises(self, supervisor, equipment, future_date):
        """EQ-04: PATCH/close on CERRADA → WorkOrderClosedError (REQ-05)."""
        order = WorkOrdersService.create_work_order(
            data={
                "tipo": "CORRECTIVO",
                "descripcion": "Test",
                "fecha_inicio": timezone.now(),
                "fk_equipo_id": equipment.id_unico,
            },
            actor=supervisor,
        )
        WorkOrdersService.close_work_order(id_orden=order.id_orden, data={}, actor=supervisor)
        with pytest.raises(WorkOrderClosedError):
            WorkOrdersService.close_work_order(
                id_orden=order.id_orden, data={}, actor=supervisor
            )

    def test_close_with_spare_parts_decrements_stock(self, supervisor, equipment, spare_part):
        """REQ-04/REQ-12: stock decremented atomically on close."""
        order = WorkOrdersService.create_work_order(
            data={
                "tipo": "CORRECTIVO",
                "descripcion": "Reparacion",
                "fecha_inicio": timezone.now(),
                "fk_equipo_id": equipment.id_unico,
            },
            actor=supervisor,
        )
        WorkOrdersService.close_work_order(
            id_orden=order.id_orden,
            data={"spare_parts_used": [{"spare_part_id": spare_part.id_repuesto, "cantidad_usada": 2}]},
            actor=supervisor,
        )
        spare_part.refresh_from_db()
        assert spare_part.cantidad_stock == 3

    def test_close_insufficient_stock_rolls_back(self, supervisor, equipment, spare_part):
        """EQ-03: insufficient stock → InsufficientStockError, full rollback."""
        from apps.inventory.exceptions import InsufficientStockError as InvError
        from apps.work_orders.exceptions import InsufficientStockError

        order = WorkOrdersService.create_work_order(
            data={
                "tipo": "CORRECTIVO",
                "descripcion": "Falla",
                "fecha_inicio": timezone.now(),
                "fk_equipo_id": equipment.id_unico,
            },
            actor=supervisor,
        )
        with pytest.raises((InsufficientStockError, InvError)):
            WorkOrdersService.close_work_order(
                id_orden=order.id_orden,
                data={
                    "spare_parts_used": [
                        {"spare_part_id": spare_part.id_repuesto, "cantidad_usada": 999}
                    ]
                },
                actor=supervisor,
            )
        # Order must remain in original state (not CERRADA)
        order.refresh_from_db()
        assert order.estado != "CERRADA"
        # Stock must be unchanged
        spare_part.refresh_from_db()
        assert spare_part.cantidad_stock == 5


@pytest.mark.django_db
class TestUpdateWorkOrder:
    def test_update_closed_order_raises(self, supervisor, equipment):
        """REQ-05: update on CERRADA order → WorkOrderClosedError."""
        order = WorkOrdersService.create_work_order(
            data={
                "tipo": "CORRECTIVO",
                "descripcion": "Test",
                "fecha_inicio": timezone.now(),
                "fk_equipo_id": equipment.id_unico,
            },
            actor=supervisor,
        )
        WorkOrdersService.close_work_order(id_orden=order.id_orden, data={}, actor=supervisor)
        with pytest.raises(WorkOrderClosedError):
            WorkOrdersService.update_work_order(
                id_orden=order.id_orden,
                data={"descripcion": "Cambio no permitido"},
                actor=supervisor,
            )


@pytest.mark.django_db
class TestRecurringOrders:
    def test_close_preventivo_recurring_generates_next(self, supervisor, equipment):
        """REQ-03: closing a MENSUAL preventivo generates next order."""
        order = WorkOrdersService.create_work_order(
            data={
                "tipo": "PREVENTIVO",
                "descripcion": "Preventivo mensual",
                "fecha_inicio": timezone.now() + timezone.timedelta(days=1),
                "frecuencia": "MENSUAL",
                "fk_equipo_id": equipment.id_unico,
            },
            actor=supervisor,
        )
        # Move to EN_PROCESO first
        WorkOrder.objects.filter(id_orden=order.id_orden).update(estado="EN_PROCESO")
        WorkOrdersService.close_work_order(id_orden=order.id_orden, data={}, actor=supervisor)

        next_orders = WorkOrder.objects.filter(
            fk_equipo_id=equipment.id_unico,
            tipo="PREVENTIVO",
            estado="PROGRAMADO",
        ).exclude(id_orden=order.id_orden)
        assert next_orders.exists()
        next_order = next_orders.first()
        assert next_order.fk_tecnico_id is None  # unassigned
