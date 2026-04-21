"""Business logic for the users app."""

from django.db import transaction

from apps.users.exceptions import DuplicateUsernameError, UserNotFoundError
from apps.users.models import User
from apps.users.repositories.users_repository import UsersRepository


class UsersService:
    @staticmethod
    @transaction.atomic
    def create_user(data: dict, actor: User) -> User:
        """Create a new GMAO user.

        Args:
            data: Validated input from UserCreateSerializer.
            actor: The supervisor performing the action.

        Raises:
            DuplicateUsernameError: If the username is already taken.
        """
        from apps.audit.services.audit_service import AuditService

        if UsersRepository.exists_by_username(data["username"]):
            raise DuplicateUsernameError(f"El usuario '{data['username']}' ya existe.")

        user = UsersRepository.create(
            username=data["username"],
            password=data["password"],
            email=data.get("email", ""),
            nombre_completo=data["nombre_completo"],
            rol=data["rol"],
        )

        AuditService.log(
            action="CREATE_USER",
            entity="User",
            entity_id=str(user.id),
            actor=actor,
            details={"username": user.username, "rol": user.rol},
        )
        return user

    @staticmethod
    @transaction.atomic
    def update_user(user_id: int, data: dict, actor: User) -> User:
        """Partially update a user's mutable fields.

        Args:
            user_id: PK of the user to update.
            data:    Validated input from UserUpdateSerializer.
            actor:   The supervisor performing the action.

        Raises:
            UserNotFoundError: If user_id does not exist.
        """
        from apps.audit.services.audit_service import AuditService

        user = UsersRepository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"Usuario {user_id} no encontrado.")

        updated = UsersRepository.update(user, data)

        AuditService.log(
            action="UPDATE_USER",
            entity="User",
            entity_id=str(updated.id),
            actor=actor,
            details=data,
        )
        return updated

    @staticmethod
    @transaction.atomic
    def deactivate_user(user_id: int, actor: User) -> User:
        """Deactivate (soft-delete) a user.

        Raises:
            UserNotFoundError: If user_id does not exist.
        """
        from apps.audit.services.audit_service import AuditService

        user = UsersRepository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"Usuario {user_id} no encontrado.")

        updated = UsersRepository.update(user, {"is_active": False})

        AuditService.log(
            action="DEACTIVATE_USER",
            entity="User",
            entity_id=str(updated.id),
            actor=actor,
            details={"username": updated.username},
        )
        return updated

    @staticmethod
    def get_user(user_id: int) -> User:
        """Return a user or raise UserNotFoundError."""
        user = UsersRepository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"Usuario {user_id} no encontrado.")
        return user

    @staticmethod
    def list_users() -> "list[User]":
        """Return all users."""
        return UsersRepository.list_all()
