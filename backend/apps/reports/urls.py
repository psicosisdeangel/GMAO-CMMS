from django.urls import path

from apps.reports.controllers.reports_controller import DashboardController, MTTRReportController

urlpatterns = [
    path("dashboard/", DashboardController.as_view(), name="dashboard"),
    path("mttr/", MTTRReportController.as_view(), name="mttr-report"),
]
