"""Unit tests for EquipmentService (REQ-01)."""

import pytest

from apps.equipment.exceptions import (
    DuplicateEquipmentIdError,
    EquipmentIdImmutableError,
    EquipmentNotFoundError,
)
from apps.equipment.services.equipment_service import EquipmentService


@pytest.fixture
def supervisor(db):
    from apps.users.models import User

    return User.objects.create_user(
        username="eq_supervisor",
        password="pass",
        nombre_completo="Supervisor",
        rol="SUPERVISOR",
    )


@pytest.fixture
def valid_equipment_data():
    return {
        "id_unico": "EQ-001",
        "nombre": "Compresor A",
        "tipo": "Compresor",
        "ubicacion": "Sala de máquinas",
        "descripcion": "Compresor industrial",
    }


@pytest.mark.django_db
class TestEquipmentServiceCreate:
    def test_create_equipment_success(self, valid_equipment_data, supervisor):
        eq = EquipmentService.create_equipment(data=valid_equipment_data, actor=supervisor)
        assert eq.id_unico == "EQ-001"
        assert eq.nombre == "Compresor A"

    def test_duplicate_id_raises(self, valid_equipment_data, supervisor):
        EquipmentService.create_equipment(data=valid_equipment_data, actor=supervisor)
        with pytest.raises(DuplicateEquipmentIdError):
            EquipmentService.create_equipment(data=valid_equipment_data, actor=supervisor)


@pytest.mark.django_db
class TestEquipmentServiceUpdate:
    def test_update_equipment_success(self, valid_equipment_data, supervisor):
        EquipmentService.create_equipment(data=valid_equipment_data, actor=supervisor)
        updated = EquipmentService.update_equipment(
            id_unico="EQ-001",
            data={"nombre": "Compresor B"},
            actor=supervisor,
        )
        assert updated.nombre == "Compresor B"

    def test_update_id_unico_raises(self, valid_equipment_data, supervisor):
        """REQ-01: id_unico is immutable."""
        EquipmentService.create_equipment(data=valid_equipment_data, actor=supervisor)
        with pytest.raises(EquipmentIdImmutableError):
            EquipmentService.update_equipment(
                id_unico="EQ-001",
                data={"id_unico": "EQ-999"},
                actor=supervisor,
            )

    def test_update_nonexistent_raises(self, supervisor):
        with pytest.raises(EquipmentNotFoundError):
            EquipmentService.update_equipment(
                id_unico="GHOST",
                data={"nombre": "X"},
                actor=supervisor,
            )


@pytest.mark.django_db
class TestEquipmentServiceDelete:
    def test_delete_equipment_success(self, valid_equipment_data, supervisor):
        EquipmentService.create_equipment(data=valid_equipment_data, actor=supervisor)
        EquipmentService.delete_equipment(id_unico="EQ-001", actor=supervisor)
        with pytest.raises(EquipmentNotFoundError):
            EquipmentService.get_equipment("EQ-001")

    def test_delete_nonexistent_raises(self, supervisor):
        with pytest.raises(EquipmentNotFoundError):
            EquipmentService.delete_equipment(id_unico="GHOST", actor=supervisor)

    def test_delete_with_active_orders_raises(self, valid_equipment_data, supervisor):
        from apps.equipment.exceptions import EquipmentHasActiveOrdersError
        from apps.work_orders.models import WorkOrder
        from django.utils import timezone

        EquipmentService.create_equipment(data=valid_equipment_data, actor=supervisor)
        from apps.equipment.models import Equipment
        eq = Equipment.objects.get(id_unico="EQ-001")
        WorkOrder.objects.create(
            tipo="CORRECTIVO", estado="EN_PROCESO", descripcion="Activa",
            fecha_inicio=timezone.now(), fk_equipo=eq, fk_tecnico=supervisor,
        )
        with pytest.raises(EquipmentHasActiveOrdersError):
            EquipmentService.delete_equipment(id_unico="EQ-001", actor=supervisor)


@pytest.mark.django_db
class TestEquipmentServiceGet:
    def test_get_equipment_not_found_raises(self):
        with pytest.raises(EquipmentNotFoundError):
            EquipmentService.get_equipment("GHOST")

    def test_list_equipment_with_tipo_filter(self, valid_equipment_data, supervisor):
        EquipmentService.create_equipment(data=valid_equipment_data, actor=supervisor)
        result = list(EquipmentService.list_equipment(tipo="Compresor"))
        assert any(e.id_unico == "EQ-001" for e in result)

    def test_list_equipment_with_search_filter(self, valid_equipment_data, supervisor):
        EquipmentService.create_equipment(data=valid_equipment_data, actor=supervisor)
        result = list(EquipmentService.list_equipment(search="Compresor A"))
        assert any(e.id_unico == "EQ-001" for e in result)

    def test_list_equipment_with_ubicacion_filter(self, valid_equipment_data, supervisor):
        EquipmentService.create_equipment(data=valid_equipment_data, actor=supervisor)
        result = list(EquipmentService.list_equipment(ubicacion="Sala de máquinas"))
        assert any(e.id_unico == "EQ-001" for e in result)
