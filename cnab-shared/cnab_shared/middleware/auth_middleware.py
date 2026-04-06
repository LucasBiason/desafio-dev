"""JWT authentication middleware that validates tokens via user-service."""

import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from ..services.user_service import UserService

logger = logging.getLogger(__name__)

EXCLUDED_PATHS = ["/", "/health", "/docs", "/redoc", "/openapi.json"]


class AuthMiddleware(BaseHTTPMiddleware):
    """Validates Bearer tokens on all routes except those in EXCLUDED_PATHS."""

    def __init__(self, app) -> None:
        super().__init__(app)
        self.user_service = UserService()

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Checks the Authorization header and validates the token against user-service.

        Populates request.state.user with user data on success. Returns 401
        for missing/invalid tokens and 503 when user-service is unreachable.
        """
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        authorization = request.headers.get("Authorization")

        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Missing or invalid authorization header."},
            )

        token = authorization.split(" ", 1)[1]

        try:
            user_data = self.user_service.validate_token(token)
        except ConnectionError as exc:
            logger.error("User service unavailable while validating token: %s", exc)
            return JSONResponse(
                status_code=503,
                content={"error": "Authentication service temporarily unavailable."},
            )

        if user_data is None:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or expired token."},
            )

        request.state.user = user_data

        return await call_next(request)
