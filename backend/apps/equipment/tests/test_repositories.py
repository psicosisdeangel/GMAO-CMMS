"""Tests for EquipmentRepository."""

import pytest

from apps.equipment.repositories.equipment_repository import EquipmentRepository


@pytest.mark.django_db
class TestEquipmentRepository:
    def test_create_and_get(self):
        eq = EquipmentRepository.create(
            {
                "id_unico": "EQ-REPO-001",
                "nombre": "Motor X",
                "tipo": "Motor",
                "ubicacion": "Planta 1",
            }
        )
        found = EquipmentRepository.get_by_id("EQ-REPO-001")
        assert found is not None
        assert found.nombre == "Motor X"

    def test_exists_by_id_unico(self):
        EquipmentRepository.create(
            {"id_unico": "EQ-EXIST", "nombre": "X", "tipo": "T", "ubicacion": "U"}
        )
        assert EquipmentRepository.exists_by_id_unico("EQ-EXIST") is True
        assert EquipmentRepository.exists_by_id_unico("EQ-GHOST") is False

    def test_list_all_with_filter(self):
        EquipmentRepository.create(
            {"id_unico": "EQ-F1", "nombre": "Motor A", "tipo": "Motor", "ubicacion": "Zona 1"}
        )
        EquipmentRepository.create(
            {"id_unico": "EQ-F2", "nombre": "Bomba A", "tipo": "Bomba", "ubicacion": "Zona 2"}
        )
        motors = EquipmentRepository.list_all(tipo="Motor")
        assert all(e.tipo == "Motor" for e in motors)
