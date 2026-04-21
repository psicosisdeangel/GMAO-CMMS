from django.urls import path

from apps.equipment.controllers.equipment_controller import (
    EquipmentDetailController,
    EquipmentListCreateController,
)

urlpatterns = [
    path("", EquipmentListCreateController.as_view(), name="equipment-list-create"),
    path("<str:id_unico>/", EquipmentDetailController.as_view(), name="equipment-detail"),
]
