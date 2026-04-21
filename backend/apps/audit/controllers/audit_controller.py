"""HTTP controller for audit logs — read-only (REQ-13)."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.repositories.audit_repository import AuditRepository
from apps.audit.serializers import AuditLogReadSerializer
from apps.authentication.permissions import HasRole


class AuditLogListController(APIView):
    """GET /api/audit/ — paginated, read-only list of audit logs (SUPERVISOR)."""

    permission_classes = [HasRole("SUPERVISOR")]

    @extend_schema(responses=AuditLogReadSerializer(many=True))
    def get(self, request: Request) -> Response:
        entity_filter = request.query_params.get("entity")
        action_filter = request.query_params.get("action")
        logs = AuditRepository.list_all(entity=entity_filter, action=action_filter)
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(list(logs), request)
        return paginator.get_paginated_response(AuditLogReadSerializer(page, many=True).data)
