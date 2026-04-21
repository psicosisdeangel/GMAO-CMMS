"""Authentication business logic."""

from typing import Optional

from django.contrib.auth import authenticate

from apps.users.models import User


class AuthService:
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """Validate credentials and return the User, or None if invalid.

        Args:
            username: Plain-text username.
            password: Plain-text password (compared against bcrypt hash).

        Returns:
            The User instance if credentials are valid and the account is
            active, None otherwise.
        """
        user = authenticate(username=username, password=password)
        if user is None or not user.is_active:
            return None
        return user
