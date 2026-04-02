"""Custom exceptions module for CNAB microservices."""

from .exceptions import (
    AuthenticationError,
    DatabaseError,
    DuplicateResourceError,
    MissingAuthorizationHeaderError,
    PermissionDeniedError,
    ResourceNotFoundError,
    TokenExpiredError,
    ValidationError,
)

__all__ = [
    "AuthenticationError",
    "DatabaseError",
    "DuplicateResourceError",
    "MissingAuthorizationHeaderError",
    "PermissionDeniedError",
    "ResourceNotFoundError",
    "TokenExpiredError",
    "ValidationError",
]
