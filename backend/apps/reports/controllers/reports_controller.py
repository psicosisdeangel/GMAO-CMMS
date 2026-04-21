"""HTTP controllers for reports and dashboard (REQ-09, REQ-11)."""

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.permissions import HasRole
from apps.reports.services.reports_service import ReportsService


class DashboardController(APIView):
    """GET /api/reports/dashboard/ — SUPERVISOR only (REQ-11)."""

    permission_classes = [HasRole("SUPERVISOR")]

    @extend_schema(
        responses=inline_serializer(
            name="DashboardResponse",
            fields={
                "total_equipos": serializers.IntegerField(),
                "ordenes_por_estado": serializers.DictField(),
                "mttr_ultimos_30_dias_horas": serializers.FloatField(allow_null=True),
                "fallas_por_equipo": serializers.ListField(),
            },
        )
    )
    def get(self, request: Request) -> Response:
        data = ReportsService.get_dashboard_data()
        return Response(data)


class MTTRReportController(APIView):
    """GET /api/reports/mttr/?month=YYYY-MM — SUPERVISOR only (REQ-09)."""

    permission_classes = [HasRole("SUPERVISOR")]

    @extend_schema(
        responses=inline_serializer(
            name="MTTRResponse",
            fields={
                "month": serializers.CharField(),
                "total_ordenes_correctivas_cerradas": serializers.IntegerField(),
                "mttr_horas": serializers.FloatField(allow_null=True),
            },
        )
    )
    def get(self, request: Request) -> Response:
        month = request.query_params.get("month")
        data = ReportsService.get_mttr_report(month=month)
        return Response(data)
