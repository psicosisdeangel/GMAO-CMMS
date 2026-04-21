"""HTTP controllers for the inventory app."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.permissions import HasRole
from apps.inventory.exceptions import DuplicateSparePartCodeError, SparePartNotFoundError
from apps.inventory.serializers import (
    SparePartCreateSerializer,
    SparePartReadSerializer,
    SparePartUpdateSerializer,
)
from apps.inventory.services.inventory_service import InventoryService


class SparePartListCreateController(APIView):
    """GET  /api/inventory/ — list (TECNICO|SUPERVISOR)
    POST /api/inventory/ — create (SUPERVISOR)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [HasRole("SUPERVISOR")()]
        return [HasRole("TECNICO", "SUPERVISOR")()]

    @extend_schema(responses=SparePartReadSerializer(many=True))
    def get(self, request: Request) -> Response:
        parts = InventoryService.list_spare_parts()
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(list(parts), request)
        return paginator.get_paginated_response(SparePartReadSerializer(page, many=True).data)

    @extend_schema(request=SparePartCreateSerializer, responses=SparePartReadSerializer)
    def post(self, request: Request) -> Response:
        serializer = SparePartCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            part = InventoryService.create_spare_part(
                data=serializer.validated_data,
                actor=request.user,
            )
        except DuplicateSparePartCodeError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(SparePartReadSerializer(part).data, status=status.HTTP_201_CREATED)


class SparePartDetailController(APIView):
    """GET   /api/inventory/<id>/ (TECNICO|SUPERVISOR)
    PATCH /api/inventory/<id>/ (SUPERVISOR)
    """

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [HasRole("SUPERVISOR")()]
        return [HasRole("TECNICO", "SUPERVISOR")()]

    def get(self, request: Request, id_repuesto: int) -> Response:
        try:
            part = InventoryService.get_spare_part(id_repuesto)
        except SparePartNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(SparePartReadSerializer(part).data)

    def patch(self, request: Request, id_repuesto: int) -> Response:
        serializer = SparePartUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            part = InventoryService.update_spare_part(
                id_repuesto=id_repuesto,
                data=serializer.validated_data,
                actor=request.user,
            )
        except SparePartNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(SparePartReadSerializer(part).data)
