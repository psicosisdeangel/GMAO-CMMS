"""Domain exceptions for the inventory app."""


class SparePartNotFoundError(Exception):
    """Raised when a requested spare part does not exist."""


class InsufficientStockError(Exception):
    """Raised when there is not enough stock to fulfill the request."""


class DuplicateSparePartCodeError(Exception):
    """Raised when the spare part code already exists."""
