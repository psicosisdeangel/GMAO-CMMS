"""Domain exceptions for the work_orders app."""


class WorkOrderNotFoundError(Exception):
    """Raised when a requested work order does not exist."""


class WorkOrderClosedError(Exception):
    """Raised when attempting to modify a CERRADA work order (REQ-05 → HTTP 422)."""


class WorkOrderInvalidDateError(Exception):
    """Raised when fecha_inicio is in the past (REQ-02)."""


class WorkOrderInvalidTransitionError(Exception):
    """Raised when a state transition is not allowed."""


class InsufficientStockError(Exception):
    """Raised when a spare part does not have enough stock."""
