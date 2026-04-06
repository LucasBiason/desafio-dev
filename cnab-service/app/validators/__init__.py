"""FastAPI dependency validators for cnab-service."""

from .fernet_middleware import require_service_token

__all__ = ["require_service_token"]
