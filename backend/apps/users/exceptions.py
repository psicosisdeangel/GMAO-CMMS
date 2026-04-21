"""Domain exceptions for the users app."""


class DuplicateUsernameError(Exception):
    """Raised when a username already exists."""


class UserNotFoundError(Exception):
    """Raised when a requested user does not exist."""
