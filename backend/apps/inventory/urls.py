from django.urls import path

from apps.inventory.controllers.inventory_controller import (
    SparePartDetailController,
    SparePartListCreateController,
)

urlpatterns = [
    path("", SparePartListCreateController.as_view(), name="spare-part-list-create"),
    path(
        "<int:id_repuesto>/",
        SparePartDetailController.as_view(),
        name="spare-part-detail",
    ),
]
