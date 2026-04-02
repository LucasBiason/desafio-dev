"""Shared package for CNAB Parser FastAPI microservices."""

from cnab_shared.setup_api import CNABFastAPI
from cnab_shared.database.database import get_db, Base, get_engine
from cnab_shared.models.base_model import BaseModel
from cnab_shared.repository.base_repository import BaseRepository
from cnab_shared.exceptions.exceptions import (
    AuthenticationError,
    TokenExpiredError,
    ValidationError,
    DatabaseError,
    PermissionDeniedError,
    ResourceNotFoundError,
    DuplicateResourceError,
    MissingAuthorizationHeaderError,
)
from cnab_shared.middleware.auth_middleware import AuthMiddleware
from cnab_shared.middleware.exceptions_middleware import CatchExceptionsMiddleware
from cnab_shared.middleware.logging_middleware import LoggingMiddleware
from cnab_shared.routers.health_router import create_health_router
from cnab_shared.services.user_service import UserService
from cnab_shared.logging.config import configure_logging, get_logger

__all__ = [
    "CNABFastAPI",
    "get_db",
    "Base",
    "get_engine",
    "BaseModel",
    "BaseRepository",
    "AuthenticationError",
    "TokenExpiredError",
    "ValidationError",
    "DatabaseError",
    "PermissionDeniedError",
    "ResourceNotFoundError",
    "DuplicateResourceError",
    "MissingAuthorizationHeaderError",
    "AuthMiddleware",
    "CatchExceptionsMiddleware",
    "LoggingMiddleware",
    "create_health_router",
    "UserService",
    "configure_logging",
    "get_logger",
]
