"""Request/response logging middleware."""

import logging
import time

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """Logs all incoming requests and outgoing responses with timing."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(
            ">>> %s %s (client: %s)",
            request.method,
            request.path,
            request.META.get("REMOTE_ADDR", "unknown"),
        )

        start_time = time.time()
        response = self.get_response(request)
        process_time = time.time() - start_time

        logger.info(
            "<<< %s %s [%d] (%.3fs)",
            request.method,
            request.path,
            response.status_code,
            process_time,
        )

        return response
