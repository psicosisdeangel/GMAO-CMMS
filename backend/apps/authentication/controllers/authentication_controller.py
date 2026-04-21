"""HTTP controllers for authentication."""

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.serializers import LoginSerializer
from apps.authentication.services.authentication_service import AuthService
from apps.users.serializers import UserCreateSerializer, UserReadSerializer, UserRegisterSerializer
from apps.users.services.users_service import UsersService
from apps.users.exceptions import DuplicateUsernameError


class RegisterController(APIView):
    """POST /api/auth/register/ — public endpoint, creates a new TECNICO account."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegisterSerializer,
        responses=inline_serializer(
            name="RegisterResponse",
            fields={
                "access": serializers.CharField(),
                "refresh": serializers.CharField(),
                "user": inline_serializer(
                    name="RegisterUser",
                    fields={
                        "id": serializers.IntegerField(),
                        "username": serializers.CharField(),
                        "nombre_completo": serializers.CharField(),
                        "rol": serializers.CharField(),
                    },
                ),
            },
        ),
    )
    def post(self, request: Request) -> Response:
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {**serializer.validated_data, "rol": "TECNICO"}
        try:
            user = UsersService.create_user(data=data, actor=None)
        except DuplicateUsernameError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)

        refresh = RefreshToken.for_user(user)
        refresh["rol"] = user.rol
        refresh["username"] = user.username
        refresh["nombre_completo"] = user.nombre_completo

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "nombre_completo": user.nombre_completo,
                    "rol": user.rol,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginController(APIView):
    """POST /api/auth/login/ — public endpoint, no authentication required."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses=inline_serializer(
            name="LoginResponse",
            fields={
                "access": serializers.CharField(),
                "refresh": serializers.CharField(),
                "user": inline_serializer(
                    name="LoginUser",
                    fields={
                        "id": serializers.IntegerField(),
                        "username": serializers.CharField(),
                        "nombre_completo": serializers.CharField(),
                        "rol": serializers.CharField(),
                    },
                ),
            },
        ),
    )
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = AuthService.authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response(
                {"error": "Credenciales inválidas o cuenta desactivada."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        # Embed custom claims into the access token
        refresh["rol"] = user.rol
        refresh["username"] = user.username
        refresh["nombre_completo"] = user.nombre_completo

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "nombre_completo": user.nombre_completo,
                    "rol": user.rol,
                },
            },
            status=status.HTTP_200_OK,
        )
