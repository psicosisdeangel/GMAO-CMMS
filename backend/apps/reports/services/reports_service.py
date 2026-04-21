"""Business logic for reports and dashboard (REQ-09, REQ-11)."""

from datetime import datetime, timedelta
from typing import Optional

from django.db.models import Avg, Count, ExpressionWrapper, F, FloatField, Q
from django.utils import timezone


class ReportsService:
    @staticmethod
    def get_dashboard_data() -> dict:
        """Aggregate dashboard data for SUPERVISOR (REQ-11).

        Returns a dict with:
        - total_equipos
        - ordenes_por_estado: {PROGRAMADO, EN_PROCESO, CERRADA}
        - mttr_last_30_days: mean time to repair in hours (corrective only)
        - fallas_por_equipo: top 10 equipment by corrective orders (last 30 days)
        """
        from apps.equipment.models import Equipment
        from apps.work_orders.models import WorkOrder

        total_equipos = Equipment.objects.count()

        ordenes_por_estado = {
            estado: WorkOrder.objects.filter(estado=estado).count()
            for estado in ["PROGRAMADO", "EN_PROCESO", "CERRADA"]
        }

        thirty_days_ago = timezone.now() - timedelta(days=30)

        # MTTR for last 30 days (corrective closed orders)
        closed_corrective = WorkOrder.objects.filter(
            tipo="CORRECTIVO",
            estado="CERRADA",
            fecha_cierre__gte=thirty_days_ago,
            fecha_cierre__isnull=False,
        )
        mttr_hours = ReportsService._calculate_mttr_hours(closed_corrective)

        # Failure frequency per equipment (last 30 days)
        fallas_por_equipo = list(
            WorkOrder.objects.filter(
                tipo="CORRECTIVO",
                fecha_inicio__gte=thirty_days_ago,
            )
            .values("fk_equipo_id", "fk_equipo__nombre")
            .annotate(total_fallas=Count("id_orden"))
            .order_by("-total_fallas")[:10]
        )

        return {
            "total_equipos": total_equipos,
            "ordenes_por_estado": ordenes_por_estado,
            "mttr_ultimos_30_dias_horas": mttr_hours,
            "fallas_por_equipo": [
                {
                    "equipo_id": row["fk_equipo_id"],
                    "equipo_nombre": row["fk_equipo__nombre"],
                    "total_fallas": row["total_fallas"],
                }
                for row in fallas_por_equipo
            ],
        }

    @staticmethod
    def get_mttr_report(month: Optional[str] = None) -> dict:
        """Calculate MTTR for a given month (REQ-09).

        Args:
            month: ISO format "YYYY-MM".  Defaults to current month.

        Returns:
            Dict with month, total_corrective_orders, mttr_hours.
        """
        from apps.work_orders.models import WorkOrder

        if month:
            try:
                year, m = month.split("-")
                start = timezone.make_aware(datetime(int(year), int(m), 1))
            except (ValueError, AttributeError):
                start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            now = timezone.now()
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # End of month
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)

        closed_corrective = WorkOrder.objects.filter(
            tipo="CORRECTIVO",
            estado="CERRADA",
            fecha_cierre__gte=start,
            fecha_cierre__lt=end,
        )

        mttr_hours = ReportsService._calculate_mttr_hours(closed_corrective)

        return {
            "month": start.strftime("%Y-%m"),
            "total_ordenes_correctivas_cerradas": closed_corrective.count(),
            "mttr_horas": mttr_hours,
        }

    @staticmethod
    def _calculate_mttr_hours(queryset) -> Optional[float]:
        """Compute MTTR in hours from a queryset of closed corrective orders.

        MTTR = sum(fecha_cierre - fecha_inicio) / count
        """
        records = queryset.filter(fecha_cierre__isnull=False).values(
            "fecha_inicio", "fecha_cierre"
        )
        if not records:
            return None

        total_seconds = sum(
            (r["fecha_cierre"] - r["fecha_inicio"]).total_seconds() for r in records
        )
        count = len(records)
        if count == 0:
            return None
        return round(total_seconds / count / 3600, 2)
