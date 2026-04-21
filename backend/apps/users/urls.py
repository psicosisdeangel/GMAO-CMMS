from django.urls import path

from apps.users.controllers.users_controller import UserDetailController, UserListCreateController

urlpatterns = [
    path("", UserListCreateController.as_view(), name="user-list-create"),
    path("<int:user_id>/", UserDetailController.as_view(), name="user-detail"),
]
