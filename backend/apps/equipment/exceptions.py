"""Domain exceptions for the equipment app."""


class DuplicateEquipmentIdError(Exception):
    """Raised when id_unico already exists (REQ-01)."""


class EquipmentNotFoundError(Exception):
    """Raised when the requested equipment does not exist."""


class EquipmentIdImmutableError(Exception):
    """Raised when a PATCH/PUT tries to change id_unico (REQ-01)."""


class EquipmentHasActiveOrdersError(Exception):
    """Raised when trying to delete equipment with active work orders."""
