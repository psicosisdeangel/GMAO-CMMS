from django.urls import path

from apps.audit.controllers.audit_controller import AuditLogListController

urlpatterns = [
    path("", AuditLogListController.as_view(), name="audit-list"),
]
