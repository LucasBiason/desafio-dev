"""Exception handler tests."""

from unittest.mock import patch

import pytest
from django.test import RequestFactory, override_settings
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response

from core.handlers import exception_handler


@pytest.fixture
def rf():
    """RequestFactory instance."""
    return RequestFactory()


class TestExceptionHandler:
    """exception_handler function."""

    def test_validation_error_returns_400(self, rf) -> None:
        """ValidationError returns 400."""
        exc = ValidationError({"field": "This field is required."})
        request = rf.get("/")
        context = {"request": request, "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["code"] == 400
        assert "time" in response.data

    def test_not_found_returns_404(self, rf) -> None:
        """NotFound returns 404."""
        exc = NotFound("Resource not found.")
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_permission_denied_returns_403(self, rf) -> None:
        """PermissionDenied returns 403."""
        exc = PermissionDenied("Access denied.")
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_http404_converted_to_not_found(self, rf) -> None:
        """Django Http404 is converted to a 404 response."""
        from django.http import Http404

        exc = Http404("Page not found.")
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_django_permission_denied_converted(self, rf) -> None:
        """Django PermissionDenied is converted to 403."""
        from django.core.exceptions import PermissionDenied as DjangoPermissionDenied

        exc = DjangoPermissionDenied("Permission denied.")
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_generic_api_exception_with_string_detail(self, rf) -> None:
        """NotAuthenticated returns 401."""
        exc = NotAuthenticated("Not authenticated.")
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_response_contains_required_fields(self, rf) -> None:
        """Response body includes code, detail, status and time."""
        exc = NotFound("Not found.")
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert "code" in response.data
        assert "detail" in response.data
        assert "status" in response.data
        assert "time" in response.data

    @override_settings(DEBUG=True)
    def test_debug_mode_includes_traceback(self, rf) -> None:
        """DEBUG=True adds traceback to the response."""
        exc = NotFound("Not found.")
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert "traceback" in response.data

    @override_settings(DEBUG=False)
    def test_production_mode_excludes_traceback(self, rf) -> None:
        """DEBUG=False omits traceback from the response."""
        exc = NotFound("Not found.")
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert "traceback" not in response.data

    def test_unhandled_exception_returns_500_json(self, rf) -> None:
        """Unhandled exception returns 500 with InternalServerError status."""
        exc = ValueError("Some value error.")
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 500
        assert response.data["code"] == 500
        assert response.data["status"] == "InternalServerError"

    def test_api_exception_with_list_detail(self, rf) -> None:
        """APIException with list detail returns 400."""

        class ListDetailException(APIException):
            status_code = 400
            default_detail = ["error 1", "error 2"]

        exc = ListDetailException()
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 400

    def test_api_exception_with_dict_detail(self, rf) -> None:
        """APIException with dict detail returns 400 with dict in detail."""

        class DictDetailException(APIException):
            status_code = 400
            default_detail = {"field": "This field is required."}

        exc = DictDetailException()
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 400
        assert isinstance(response.data["detail"], dict)

    @override_settings(DEBUG=True)
    def test_unhandled_exception_debug_includes_detail_and_traceback(self, rf) -> None:
        """Unhandled exception with DEBUG=True includes detail and traceback in 500."""
        exc = RuntimeError("Unexpected failure")
        context = {"request": rf.get("/boom"), "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 500
        assert response.data["detail"] == "Unexpected failure"
        assert "traceback" in response.data

    def test_django_validation_error_with_message_dict(self, rf) -> None:
        """DjangoValidationError with message_dict returns 400."""
        from django.core.exceptions import ValidationError as DjangoValidationError

        exc = DjangoValidationError({"field": ["This field is required."]})
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 400

    def test_django_validation_error_with_messages_list(self, rf) -> None:
        """DjangoValidationError with messages list returns 400."""
        from django.core.exceptions import ValidationError as DjangoValidationError

        exc = DjangoValidationError(["Error one.", "Error two."])
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 400

    def test_django_validation_error_with_string_message(self, rf) -> None:
        """DjangoValidationError with a plain string returns 400."""
        from django.core.exceptions import ValidationError as DjangoValidationError

        exc = DjangoValidationError("Plain validation error.")
        context = {"request": rf.get("/"), "view": None}

        response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 400

    def test_django_validation_error_without_messages_or_message_dict(self, rf) -> None:
        """DjangoValidationError without messages or message_dict falls back to str(exc)."""
        from django.core.exceptions import ValidationError as DjangoValidationError

        class NoAttributesValidationError(DjangoValidationError):
            def __init__(self):
                # Do not call super().__init__ to avoid setting messages
                Exception.__init__(self, "fallback error")

            def __str__(self):
                return "fallback error"

        exc = NoAttributesValidationError()
        context = {"request": rf.get("/"), "view": None}

        # Patch hasattr inside core.handlers to return False for messages/message_dict
        original_hasattr = hasattr

        def patched_hasattr(obj, name):
            if obj is exc and name in ("message_dict", "messages"):
                return False
            return original_hasattr(obj, name)

        with patch("builtins.hasattr", side_effect=patched_hasattr):
            response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 400

    def test_non_api_exception_with_drf_response_falls_through_to_500(self, rf) -> None:
        """Non-APIException where DRF returns a response still yields 500."""
        exc = ValueError("edge case error")
        context = {"request": rf.get("/"), "view": None}

        fake_response = Response({}, status=200)

        with patch("core.handlers.drf_exception_handler", return_value=fake_response):
            response = exception_handler(exc, context)

        assert response is not None
        assert response.status_code == 500
        assert response.data["status"] == "InternalServerError"
