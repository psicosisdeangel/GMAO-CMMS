from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.authentication.controllers.authentication_controller import LoginController, RegisterController

urlpatterns = [
    path("login/", LoginController.as_view(), name="login"),
    path("register/", RegisterController.as_view(), name="register"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
