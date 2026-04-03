"""Tests for app/dependencies.py JWT auth dependency."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException


def _make_request(auth_header: str | None = None) -> MagicMock:
    """Creates a mock Request with the given Authorization header."""
    request = MagicMock()
    request.headers = {"Authorization": auth_header} if auth_header else {}
    return request


class TestRequireJwt:
    """Tests for the require_jwt dependency function."""

    def test_valid_token_returns_user_data(self):
        """require_jwt returns user data when the token is valid."""
        from app.dependencies import require_jwt

        user_data = {"id": 1, "email": "user@test.com"}
        request = _make_request("Bearer valid-token")
        with patch("app.dependencies.UserService") as mock_service:
            mock_service.return_value.validate_token.return_value = user_data
            result = require_jwt(request)
        assert result == user_data

    def test_missing_header_raises_401(self):
        """require_jwt raises HTTPException 401 when Authorization header is absent."""
        from app.dependencies import require_jwt

        request = _make_request(None)
        with pytest.raises(HTTPException) as exc_info:
            require_jwt(request)
        assert exc_info.value.status_code == 401

    def test_non_bearer_raises_401(self):
        """require_jwt raises HTTPException 401 when scheme is not Bearer."""
        from app.dependencies import require_jwt

        request = _make_request("Basic dXNlcjpwYXNz")
        with pytest.raises(HTTPException) as exc_info:
            require_jwt(request)
        assert exc_info.value.status_code == 401

    def test_connection_error_raises_503(self):
        """require_jwt raises HTTPException 503 when user-service is unreachable."""
        from app.dependencies import require_jwt

        request = _make_request("Bearer some-token")
        with patch("app.dependencies.UserService") as mock_service:
            mock_service.return_value.validate_token.side_effect = ConnectionError("down")
            with pytest.raises(HTTPException) as exc_info:
                require_jwt(request)
        assert exc_info.value.status_code == 503

    def test_invalid_token_raises_401(self):
        """require_jwt raises HTTPException 401 when user-service returns None."""
        from app.dependencies import require_jwt

        request = _make_request("Bearer bad-token")
        with patch("app.dependencies.UserService") as mock_service:
            mock_service.return_value.validate_token.return_value = None
            with pytest.raises(HTTPException) as exc_info:
                require_jwt(request)
        assert exc_info.value.status_code == 401
