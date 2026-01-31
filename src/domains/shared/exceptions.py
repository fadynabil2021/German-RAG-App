"""
Common exceptions for domain layer.
"""

class DomainException(Exception):
    """Base exception for domain errors."""
    pass

class EntityNotFoundError(DomainException):
    """Raised when an entity is not found."""
    pass

class UnauthorizedAccessError(DomainException):
    """Raised when user attempts unauthorized action."""
    pass

class ValidationError(DomainException):
    """Raised when domain validation fails."""
    pass

class ResourceQuotaExceededError(DomainException):
    """Raised when user exceeds resource limits (freemium)."""
    pass
