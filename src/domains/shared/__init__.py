"""Shared domain module."""
from .repository import BaseRepository
from .exceptions import (
    DomainException,
    EntityNotFoundError,
    UnauthorizedAccessError,
    ValidationError,
    ResourceQuotaExceededError
)

__all__ = [
    "BaseRepository",
    "DomainException",
    "EntityNotFoundError",
    "UnauthorizedAccessError",
    "ValidationError",
    "ResourceQuotaExceededError",
]
