"""Tests for InventoryService."""

import pytest

from apps.inventory.exceptions import InsufficientStockError, SparePartNotFoundError
from apps.inventory.services.inventory_service import InventoryService


@pytest.fixture
def supervisor(db):
    from apps.users.models import User

    return User.objects.create_user(
        username="inv_supervisor",
        password="pass",
        nombre_completo="Inv Sup",
        rol="SUPERVISOR",
    )


@pytest.fixture
def spare_part_data():
    return {
        "nombre": "Filtro de aceite",
        "codigo": "FLT-001",
        "descripcion": "Filtro estándar",
        "cantidad_stock": 10,
        "unidad_medida": "unidades",
    }


@pytest.mark.django_db
class TestInventoryService:
    def test_create_spare_part(self, spare_part_data, supervisor):
        part = InventoryService.create_spare_part(data=spare_part_data, actor=supervisor)
        assert part.codigo == "FLT-001"
        assert part.cantidad_stock == 10

    def test_decrement_stock(self, spare_part_data, supervisor):
        part = InventoryService.create_spare_part(data=spare_part_data, actor=supervisor)
        InventoryService.decrement_stock(id_repuesto=part.id_repuesto, cantidad=3)
        refreshed = InventoryService.get_spare_part(part.id_repuesto)
        assert refreshed.cantidad_stock == 7

    def test_insufficient_stock_raises(self, spare_part_data, supervisor):
        part = InventoryService.create_spare_part(data=spare_part_data, actor=supervisor)
        with pytest.raises(InsufficientStockError):
            InventoryService.decrement_stock(id_repuesto=part.id_repuesto, cantidad=999)

    def test_get_nonexistent_raises(self):
        with pytest.raises(SparePartNotFoundError):
            InventoryService.get_spare_part(99999)
