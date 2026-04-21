"""RBAC permission helpers (REQ-07, REQ-10).

Usage::

    class MyController(APIView):
        permission_classes = [HasRole("SUPERVISOR")]
        # or for multiple:
        permission_classes = [HasRole("TECNICO", "SUPERVISOR")]
"""

from rest_framework.permissions import BasePermission


def HasRole(*roles: str) -> type:
    """Factory that returns a DRF permission class restricted to *roles*.

    Args:
        *roles: One or more role strings (e.g. "SUPERVISOR", "TECNICO").

    Returns:
        A BasePermission subclass that grants access only to authenticated
        users whose ``rol`` field is in *roles*.
    """

    class _HasRole(BasePermission):
        allowed_roles: tuple[str, ...] = roles

        def has_permission(self, request, view) -> bool:
            return bool(
                request.user
                and request.user.is_authenticated
                and request.user.rol in self.allowed_roles
            )

    _HasRole.__name__ = f"HasRole({', '.join(roles)})"
    return _HasRole
