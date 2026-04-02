"""Middleware that catches unhandled exceptions and returns structured JSON responses."""

import logging
import traceback
from datetime import UTC, datetime

from fastapi.exceptions import ResponseValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class CatchExceptionsMiddleware(BaseHTTPMiddleware):
    """Catches all unhandled exceptions and returns structured JSON error responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Forwards the request and handles any unhandled exception with a JSON response."""
        try:
            return await call_next(request)

        except ResponseValidationError as exc:
            logger.error(
                "Response validation error at %s %s: %s",
                request.method,
                request.url.path,
                str(exc),
            )
            return JSONResponse(
                status_code=422,
                content={
                    "error": "Server response validation error.",
                    "detail": str(exc),
                    "timestamp": datetime.now(UTC).isoformat(),
                    "request_path": str(request.url.path),
                    "request_method": request.method,
                },
            )

        except Exception as exc:
            tb = traceback.format_exc()
            logger.error(
                "Unhandled exception at %s %s:\n%s",
                request.method,
                request.url.path,
                tb,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": str(exc),
                    "traceback": tb,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "request_path": str(request.url.path),
                    "request_method": request.method,
                },
            )
