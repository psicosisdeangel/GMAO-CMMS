"""Repository layer for User — all ORM access lives here."""

from typing import Optional

from apps.users.models import User


class UsersRepository:
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """Return a User by primary key, or None."""
        return User.objects.filter(id=user_id).first()

    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        """Return a User by username, or None."""
        return User.objects.filter(username=username).first()

    @staticmethod
    def list_all() -> "list[User]":
        """Return all users ordered by username."""
        return list(User.objects.all().order_by("username"))

    @staticmethod
    def create(
        username: str,
        password: str,
        email: str,
        nombre_completo: str,
        rol: str,
    ) -> User:
        """Create and persist a new User (password is hashed via set_password)."""
        user = User(
            username=username,
            email=email,
            nombre_completo=nombre_completo,
            rol=rol,
        )
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def update(user: User, data: dict) -> User:
        """Apply a dict of field updates to an existing user."""
        for field, value in data.items():
            setattr(user, field, value)
        user.save()
        return user

    @staticmethod
    def exists_by_username(username: str) -> bool:
        """Return True if a user with that username already exists."""
        return User.objects.filter(username=username).exists()
