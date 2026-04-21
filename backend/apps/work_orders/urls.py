from django.urls import path

from apps.work_orders.controllers.work_orders_controller import (
    EquipmentHistoryController,
    WorkOrderCloseController,
    WorkOrderDetailController,
    WorkOrderListCreateController,
    WorkOrderStartController,
)

urlpatterns = [
    path("", WorkOrderListCreateController.as_view(), name="work-order-list-create"),
    path("<int:id_orden>/", WorkOrderDetailController.as_view(), name="work-order-detail"),
    path("<int:id_orden>/close/", WorkOrderCloseController.as_view(), name="work-order-close"),
    path("<int:id_orden>/start/", WorkOrderStartController.as_view(), name="work-order-start"),
    path(
        "equipment/<str:id_unico>/history/",
        EquipmentHistoryController.as_view(),
        name="equipment-history",
    ),
]
