"""HTTP controllers for the equipment app (REQ-01)."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.permissions import HasRole
from apps.equipment.exceptions import (
    DuplicateEquipmentIdError,
    EquipmentHasActiveOrdersError,
    EquipmentIdImmutableError,
    EquipmentNotFoundError,
)
from apps.equipment.serializers import (
    EquipmentCreateSerializer,
    EquipmentReadSerializer,
    EquipmentUpdateSerializer,
)
from apps.equipment.services.equipment_service import EquipmentService


def _paginate(request, queryset, serializer_class):
    paginator = PageNumberPagination()
    paginator.page_size = 20
    page = paginator.paginate_queryset(queryset, request)
    return paginator.get_paginated_response(serializer_class(page, many=True).data)


class EquipmentListCreateController(APIView):
    """GET  /api/equipment/ — list (TECNICO|SUPERVISOR)
    POST /api/equipment/ — create (SUPERVISOR only)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [HasRole("SUPERVISOR")()]
        return [HasRole("TECNICO", "SUPERVISOR")()]

    @extend_schema(responses=EquipmentReadSerializer(many=True))
    def get(self, request: Request) -> Response:
        tipo = request.query_params.get("tipo")
        ubicacion = request.query_params.get("ubicacion")
        search = request.query_params.get("search")
        equipment_list = EquipmentService.list_equipment(tipo=tipo, ubicacion=ubicacion, search=search)
        return _paginate(request, equipment_list, EquipmentReadSerializer)

    @extend_schema(request=EquipmentCreateSerializer, responses=EquipmentReadSerializer)
    def post(self, request: Request) -> Response:
        serializer = EquipmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            equipment = EquipmentService.create_equipment(
                data=serializer.validated_data,
                actor=request.user,
            )
        except DuplicateEquipmentIdError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(EquipmentReadSerializer(equipment).data, status=status.HTTP_201_CREATED)


class EquipmentDetailController(APIView):
    """GET    /api/equipment/<id_unico>/ (TECNICO|SUPERVISOR)
    PATCH  /api/equipment/<id_unico>/ (SUPERVISOR)
    DELETE /api/equipment/<id_unico>/ (SUPERVISOR)
    """

    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [HasRole("SUPERVISOR")()]
        return [HasRole("TECNICO", "SUPERVISOR")()]

    @extend_schema(responses=EquipmentReadSerializer)
    def get(self, request: Request, id_unico: str) -> Response:
        try:
            equipment = EquipmentService.get_equipment(id_unico)
        except EquipmentNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(EquipmentReadSerializer(equipment).data)

    @extend_schema(request=EquipmentUpdateSerializer, responses=EquipmentReadSerializer)
    def patch(self, request: Request, id_unico: str) -> Response:
        serializer = EquipmentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if "id_unico" in request.data:
            return Response(
                {"error": "El campo 'id_unico' es inmutable."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            equipment = EquipmentService.update_equipment(
                id_unico=id_unico,
                data=serializer.validated_data,
                actor=request.user,
            )
        except EquipmentNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except EquipmentIdImmutableError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(EquipmentReadSerializer(equipment).data)

    def delete(self, request: Request, id_unico: str) -> Response:
        try:
            EquipmentService.delete_equipment(id_unico=id_unico, actor=request.user)
        except EquipmentNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except EquipmentHasActiveOrdersError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)
