"""Domain exceptions for the audit app."""


class AuditLogWriteError(Exception):
    """Raised when an audit log entry cannot be persisted."""
