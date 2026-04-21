"""
URL configuration for GMAO project.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/equipment/", include("apps.equipment.urls")),
    path("api/work-orders/", include("apps.work_orders.urls")),
    path("api/inventory/", include("apps.inventory.urls")),
    path("api/audit/", include("apps.audit.urls")),
    path("api/reports/", include("apps.reports.urls")),
    # OpenAPI / Swagger (REQ-15)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
