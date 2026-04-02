"""Request/response logging middleware."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs all incoming requests and outgoing responses with timing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        logger.info(
            ">>> %s %s (client: %s)",
            request.method,
            request.url.path,
            request.client.host if request.client else "unknown",
        )

        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(
                "<<< %s %s [%d] (%.3fs)",
                request.method,
                request.url.path,
                response.status_code,
                process_time,
            )
            return response
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                "!!! %s %s [%s: %s] (%.3fs)",
                request.method,
                request.url.path,
                type(exc).__name__,
                str(exc),
                process_time,
            )
            raise
