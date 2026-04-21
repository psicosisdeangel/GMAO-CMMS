"""DRF serializers for the users app.

Serializers only validate *shape* — no business logic.
"""

from rest_framework import serializers

from apps.users.models import User


class UserReadSerializer(serializers.ModelSerializer):
    """Read-only representation of a User."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "nombre_completo", "rol", "is_active", "date_joined"]
        read_only_fields = fields


class UserCreateSerializer(serializers.Serializer):
    """Input shape for creating a new user (SUPERVISOR — rol required)."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    nombre_completo = serializers.CharField(max_length=255)
    rol = serializers.ChoiceField(choices=User.Rol.choices)


class UserRegisterSerializer(serializers.Serializer):
    """Input shape for self-registration — rol is always forced to TECNICO."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    nombre_completo = serializers.CharField(max_length=255)


class UserUpdateSerializer(serializers.Serializer):
    """Input shape for partial user updates (SUPERVISOR only)."""

    email = serializers.EmailField(required=False, allow_blank=True)
    nombre_completo = serializers.CharField(max_length=255, required=False)
    is_active = serializers.BooleanField(required=False)
