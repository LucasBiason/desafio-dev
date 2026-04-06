"""FastAPI dependency for JWT authentication via user-service."""

import logging

from fastapi import HTTPException, Request

from cnab_shared.services.user_service import UserService

logger = logging.getLogger(__name__)


def require_jwt(request: Request) -> dict:
    """Validates a Bearer JWT token against the user-service.

    Raises HTTPException 401 for missing/invalid tokens and 503 when
    user-service is unreachable. Returns user data dict on success.
    """
    auth = request.headers.get("Authorization", "")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header.")

    token = auth.split(" ", 1)[1]
    user_service = UserService()

    try:
        user_data = user_service.validate_token(token)
    except ConnectionError as exc:
        logger.error("User service unavailable: %s", exc)
        raise HTTPException(status_code=503, detail="Auth service unavailable.")

    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    return user_data
