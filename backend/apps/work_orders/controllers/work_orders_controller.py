"""HTTP controllers for work orders (REQ-02, 03, 04, 05, 06)."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.permissions import HasRole
from apps.work_orders.exceptions import (
    InsufficientStockError,
    WorkOrderClosedError,
    WorkOrderInvalidDateError,
    WorkOrderInvalidTransitionError,
    WorkOrderNotFoundError,
)
from apps.work_orders.serializers import (
    WorkOrderCloseSerializer,
    WorkOrderCreateSerializer,
    WorkOrderReadSerializer,
    WorkOrderUpdateSerializer,
)
from apps.work_orders.services.work_orders_service import WorkOrdersService


def _paginate(request, queryset, serializer_class):
    paginator = PageNumberPagination()
    paginator.page_size = 20
    page = paginator.paginate_queryset(queryset, request)
    return paginator.get_paginated_response(serializer_class(page, many=True).data)


class WorkOrderListCreateController(APIView):
    """GET  /api/work-orders/  — list (TECNICO sees own; SUPERVISOR sees all)
    POST /api/work-orders/  — create
    """

    permission_classes = [HasRole("TECNICO", "SUPERVISOR")]

    @extend_schema(responses=WorkOrderReadSerializer(many=True))
    def get(self, request: Request) -> Response:
        estado = request.query_params.get("estado")
        tipo = request.query_params.get("tipo")
        equipo_id = request.query_params.get("fk_equipo")
        orders = WorkOrdersService.list_work_orders(
            actor=request.user,
            estado=estado,
            tipo=tipo,
            equipo_id=equipo_id,
        )
        return _paginate(request, orders, WorkOrderReadSerializer)

    @extend_schema(request=WorkOrderCreateSerializer, responses=WorkOrderReadSerializer)
    def post(self, request: Request) -> Response:
        serializer = WorkOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if (
            serializer.validated_data["tipo"] == "PREVENTIVO"
            and request.user.rol != "SUPERVISOR"
        ):
            return Response(
                {"error": "Solo un SUPERVISOR puede programar mantenimientos preventivos."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            order = WorkOrdersService.create_work_order(
                data=serializer.validated_data,
                actor=request.user,
            )
        except WorkOrderInvalidDateError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(WorkOrderReadSerializer(order).data, status=status.HTTP_201_CREATED)


class WorkOrderDetailController(APIView):
    """GET   /api/work-orders/<id>/
    PATCH /api/work-orders/<id>/
    """

    permission_classes = [HasRole("TECNICO", "SUPERVISOR")]

    def get(self, request: Request, id_orden: int) -> Response:
        try:
            order = WorkOrdersService.get_work_order(id_orden)
        except WorkOrderNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(WorkOrderReadSerializer(order).data)

    def patch(self, request: Request, id_orden: int) -> Response:
        serializer = WorkOrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = WorkOrdersService.update_work_order(
                id_orden=id_orden,
                data=serializer.validated_data,
                actor=request.user,
            )
        except WorkOrderNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except WorkOrderClosedError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(WorkOrderReadSerializer(order).data)


class WorkOrderCloseController(APIView):
    """POST /api/work-orders/<id>/close/ — REQ-05."""

    permission_classes = [HasRole("TECNICO", "SUPERVISOR")]

    def post(self, request: Request, id_orden: int) -> Response:
        serializer = WorkOrderCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = WorkOrdersService.close_work_order(
                id_orden=id_orden,
                data=serializer.validated_data,
                actor=request.user,
            )
        except WorkOrderNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except WorkOrderClosedError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except InsufficientStockError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(WorkOrderReadSerializer(order).data)


class WorkOrderStartController(APIView):
    """POST /api/work-orders/<id>/start/ — PROGRAMADO → EN_PROCESO."""

    permission_classes = [HasRole("TECNICO", "SUPERVISOR")]

    def post(self, request: Request, id_orden: int) -> Response:
        try:
            order = WorkOrdersService.start_work_order(id_orden=id_orden, actor=request.user)
        except WorkOrderNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except WorkOrderClosedError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except WorkOrderInvalidTransitionError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(WorkOrderReadSerializer(order).data)


class EquipmentHistoryController(APIView):
    """GET /api/work-orders/equipment/<id_unico>/history/ — REQ-06."""

    permission_classes = [HasRole("TECNICO", "SUPERVISOR")]

    def get(self, request: Request, id_unico: str) -> Response:
        history = WorkOrdersService.get_equipment_history(equipo_id=id_unico)
        return _paginate(request, history, WorkOrderReadSerializer)
