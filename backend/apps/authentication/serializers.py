"""Serializers for the authentication app."""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.models import User


class LoginSerializer(serializers.Serializer):
    """Input shape for the login endpoint."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class GmaoTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extends the standard JWT serializer to embed `rol` in the token payload.

    The frontend reads `rol` from the decoded JWT to drive UI visibility
    without extra API calls (REQ-08).
    """

    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token["rol"] = user.rol
        token["username"] = user.username
        token["nombre_completo"] = user.nombre_completo
        return token
