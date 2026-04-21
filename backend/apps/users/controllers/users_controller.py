"""HTTP controllers for the users app.

No business logic lives here — only HTTP handling and delegation
to UsersService.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.permissions import HasRole
from apps.users.exceptions import DuplicateUsernameError, UserNotFoundError
from apps.users.serializers import UserCreateSerializer, UserReadSerializer, UserUpdateSerializer
from apps.users.services.users_service import UsersService


class UserListCreateController(APIView):
    """GET /api/users/  — list users (SUPERVISOR)
    POST /api/users/ — create user (SUPERVISOR)
    """

    permission_classes = [HasRole("SUPERVISOR")]

    @extend_schema(responses=UserReadSerializer(many=True))
    def get(self, request: Request) -> Response:
        users = UsersService.list_users()
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(list(users), request)
        return paginator.get_paginated_response(UserReadSerializer(page, many=True).data)

    @extend_schema(request=UserCreateSerializer, responses=UserReadSerializer)
    def post(self, request: Request) -> Response:
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = UsersService.create_user(
                data=serializer.validated_data,
                actor=request.user,
            )
        except DuplicateUsernameError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(UserReadSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailController(APIView):
    """GET    /api/users/<id>/ — retrieve (SUPERVISOR)
    PATCH  /api/users/<id>/ — update   (SUPERVISOR)
    DELETE /api/users/<id>/ — deactivate (SUPERVISOR)
    """

    permission_classes = [HasRole("SUPERVISOR")]

    def get(self, request: Request, user_id: int) -> Response:
        try:
            user = UsersService.get_user(user_id)
        except UserNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserReadSerializer(user).data)

    def patch(self, request: Request, user_id: int) -> Response:
        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = UsersService.update_user(
                user_id=user_id,
                data=serializer.validated_data,
                actor=request.user,
            )
        except UserNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserReadSerializer(user).data)

    def delete(self, request: Request, user_id: int) -> Response:
        """Soft-delete: sets is_active=False."""
        try:
            UsersService.deactivate_user(user_id=user_id, actor=request.user)
        except UserNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
