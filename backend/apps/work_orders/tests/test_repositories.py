"""Tests for WorkOrdersRepository."""

import pytest
from django.utils import timezone

from apps.equipment.models import Equipment
from apps.users.models import User
from apps.work_orders.models import WorkOrder
from apps.work_orders.repositories.work_orders_repository import WorkOrdersRepository


@pytest.fixture
def supervisor(db):
    return User.objects.create_user(
        username="wo_repo_sup",
        password="pass",
        nombre_completo="Supervisor",
        rol="SUPERVISOR",
    )


@pytest.fixture
def equipment(db):
    return Equipment.objects.create(
        id_unico="EQ-REPO-WO", nombre="Motor", tipo="Motor", ubicacion="Zona C"
    )


@pytest.mark.django_db
class TestWorkOrdersRepository:
    def test_create_and_get(self, equipment):
        order = WorkOrdersRepository.create(
            {
                "tipo": "CORRECTIVO",
                "descripcion": "Test",
                "fecha_inicio": timezone.now(),
                "fk_equipo_id": equipment.id_unico,
            }
        )
        found = WorkOrdersRepository.get_by_id(order.id_orden)
        assert found is not None
        assert found.tipo == "CORRECTIVO"

    def test_list_filtered_by_estado(self, equipment):
        WorkOrdersRepository.create(
            {
                "tipo": "CORRECTIVO",
                "descripcion": "A",
                "fecha_inicio": timezone.now(),
                "fk_equipo_id": equipment.id_unico,
                "estado": "EN_PROCESO",
            }
        )
        WorkOrdersRepository.create(
            {
                "tipo": "CORRECTIVO",
                "descripcion": "B",
                "fecha_inicio": timezone.now(),
                "fk_equipo_id": equipment.id_unico,
                "estado": "PROGRAMADO",
            }
        )
        en_proceso = WorkOrdersRepository.list_all(estado="EN_PROCESO")
        assert all(o.estado == "EN_PROCESO" for o in en_proceso)

    def test_get_equipment_history(self, equipment):
        for i in range(3):
            WorkOrdersRepository.create(
                {
                    "tipo": "CORRECTIVO",
                    "descripcion": f"Order {i}",
                    "fecha_inicio": timezone.now(),
                    "fk_equipo_id": equipment.id_unico,
                }
            )
        history = WorkOrdersRepository.get_equipment_history(equipment.id_unico)
        assert len(history) == 3
