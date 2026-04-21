"""Tests for InventoryRepository."""

import pytest

from apps.inventory.repositories.inventory_repository import InventoryRepository


@pytest.mark.django_db
class TestInventoryRepository:
    def test_create_and_get(self):
        part = InventoryRepository.create(
            {
                "nombre": "Rodamiento",
                "codigo": "ROD-001",
                "cantidad_stock": 5,
                "unidad_medida": "unidades",
            }
        )
        found = InventoryRepository.get_by_id(part.id_repuesto)
        assert found.codigo == "ROD-001"

    def test_decrement_stock_atomic(self):
        part = InventoryRepository.create(
            {"nombre": "Tuerca", "codigo": "TCA-001", "cantidad_stock": 10}
        )
        rows = InventoryRepository.decrement_stock(part.id_repuesto, 4)
        assert rows == 1
        refreshed = InventoryRepository.get_by_id(part.id_repuesto)
        assert refreshed.cantidad_stock == 6

    def test_decrement_below_zero_updates_zero_rows(self):
        part = InventoryRepository.create(
            {"nombre": "Tornillo", "codigo": "TRN-001", "cantidad_stock": 2}
        )
        rows = InventoryRepository.decrement_stock(part.id_repuesto, 100)
        assert rows == 0  # stock not modified
