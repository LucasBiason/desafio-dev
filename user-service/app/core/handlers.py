"""Custom exception handler that converts all exceptions into standardized JSON responses."""

import logging
import traceback
from datetime import UTC, datetime

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def exception_handler(exc: Exception, context: dict) -> Response:
    """Convert any exception into a JSON response with the format:
    {"code": int, "detail": str|dict, "status": str, "time": str}

    DRF, Django, and unhandled exceptions are all normalized here.
    Never returns None — unhandled errors become HTTP 500 responses.
    """
    # Convert Django exceptions to DRF equivalents
    if isinstance(exc, Http404):
        exc = NotFound(detail=str(exc) or "Resource not found.")
    elif isinstance(exc, PermissionDenied):
        exc = DRFPermissionDenied(detail=str(exc) or "Permission denied.")
    elif isinstance(exc, DjangoValidationError):
        # Convert Django's ValidationError to DRF's ValidationError
        if hasattr(exc, "message_dict"):
            exc = DRFValidationError(detail=exc.message_dict)
        elif hasattr(exc, "messages"):
            exc = DRFValidationError(detail=exc.messages)
        else:
            exc = DRFValidationError(detail=str(exc))

    # Try DRF's default handler first
    response = drf_exception_handler(exc, context)

    now = datetime.now(tz=UTC).isoformat()

    # If DRF handler returned None, this is an unhandled exception
    if response is None:
        logger.error(
            "Unhandled exception at %s: %s",
            context.get("request", {}).path if hasattr(context.get("request", {}), "path") else "unknown",
            exc,
            exc_info=True,
        )
        payload = {
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Internal server error.",
            "status": "InternalServerError",
            "time": now,
        }
        if settings.DEBUG:
            payload["detail"] = str(exc)
            payload["traceback"] = traceback.format_exc()
        return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Build standardized payload from DRF response
    if isinstance(exc, DRFValidationError):
        http_code = status.HTTP_400_BAD_REQUEST
        status_text = "ValidationError"
        detail = exc.detail
    elif isinstance(exc, APIException):
        http_code = exc.status_code
        status_text = exc.__class__.__name__
        raw_detail = exc.detail
        if isinstance(raw_detail, dict):
            detail = raw_detail
        elif isinstance(raw_detail, list):
            detail = raw_detail[0] if raw_detail else str(exc)
        else:
            detail = str(raw_detail)
    else:
        http_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        status_text = "InternalServerError"
        detail = "Internal server error."

    payload = {
        "code": http_code,
        "detail": detail,
        "status": status_text,
        "time": now,
    }

    if settings.DEBUG:
        payload["traceback"] = traceback.format_exc()

    response.data = payload
    response.status_code = http_code
    return response
