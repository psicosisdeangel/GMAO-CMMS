"""
User model for GMAO (REQ-07).

Uses AbstractBaseUser so we control every field, including
the `rol` field (TECNICO | SUPERVISOR).
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class GmaoUserManager(BaseUserManager):
    """Custom manager for the GMAO User model."""

    def create_user(self, username: str, password: str, **extra_fields):
        if not username:
            raise ValueError("El nombre de usuario es obligatorio.")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("rol", User.Rol.SUPERVISOR)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """GMAO application user.

    Roles:
        TECNICO    — field technician, limited write access.
        SUPERVISOR — full management access (REQ-07).
    """

    class Rol(models.TextChoices):
        TECNICO = "TECNICO", "Técnico"
        SUPERVISOR = "SUPERVISOR", "Supervisor"

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    nombre_completo = models.CharField(max_length=255)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.TECNICO)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = GmaoUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["nombre_completo", "rol"]

    class Meta:
        db_table = "users"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self) -> str:
        return f"{self.username} ({self.rol})"
