"""FastAPI dependency for Fernet-based service-to-service authentication."""

from fastapi import Header

from cnab_shared.services.fernet_validator import FernetValidator


def require_service_token(x_service_token: str = Header(...)) -> dict:
    """Validates the X-Service-Token Fernet token from the request header.

    Raises HTTPException 401 when the token is absent, expired, or invalid.
    Returns the decrypted payload dict on success.
    """
    validator = FernetValidator()
    return validator.validate_token(x_service_token)
