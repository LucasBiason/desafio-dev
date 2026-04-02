"""AccessToken service tests."""

import pytest
from rest_framework.exceptions import AuthenticationFailed

from authentication.services.access_token import AccessToken
from authentication.exceptions import InvalidTokenException, TokenExpiredException


class TestAccessToken:
    """JWT token encoding and decoding."""

    def test_encode_returns_token_and_expiration(self) -> None:
        """Returns a (token, expiration) tuple."""
        token, validate = AccessToken().encode("123")

        assert isinstance(token, str)
        assert isinstance(validate, str)
        assert len(token) > 0

    def test_decode_valid_token(self) -> None:
        """Valid token decodes to expected payload."""
        access_token = AccessToken()
        token, _ = access_token.encode("456")
        payload = access_token.decode_token(token)

        assert payload["user"] == "456"
        assert "validate" in payload

    def test_decode_invalid_token_raises(self) -> None:
        """Invalid token raises InvalidTokenException."""
        with pytest.raises(InvalidTokenException):
            AccessToken().decode_token("not.a.valid.token")

    def test_validate_format_valid(self) -> None:
        """Extracts raw token from Bearer header."""
        access_token = AccessToken()
        token, _ = access_token.encode("789")
        result = access_token._validate_token_format(f"Bearer {token}")

        assert result == token

    def test_validate_format_missing_bearer(self) -> None:
        """Missing Bearer prefix raises AuthenticationFailed."""
        with pytest.raises(AuthenticationFailed):
            AccessToken()._validate_token_format("Token abc123")

    def test_validate_format_empty(self) -> None:
        """Empty token string raises AuthenticationFailed."""
        with pytest.raises(AuthenticationFailed):
            AccessToken()._validate_token_format("")

    def test_full_validate_flow(self) -> None:
        """Full Bearer token validates and sets validate_dt."""
        access_token = AccessToken()
        token, _ = access_token.encode("101")
        payload = access_token.validate(f"Bearer {token}")

        assert payload["user"] == "101"
        assert access_token.validate_dt is True

    def test_validate_expire_expired_token_raises(self) -> None:
        """Past expiration date raises TokenExpiredException."""
        access_token = AccessToken()
        past_date = "01/01/2000 00:00:00"

        with pytest.raises(TokenExpiredException):
            access_token.validate_expire(past_date)

    def test_validate_expire_invalid_format_raises(self) -> None:
        """Malformed date string raises InvalidTokenException."""
        access_token = AccessToken()

        with pytest.raises(InvalidTokenException):
            access_token.validate_expire("not-a-date")

    def test_validate_expire_sets_valid_until(self) -> None:
        """Successful validation sets valid_until on the instance."""
        from datetime import datetime, timedelta

        access_token = AccessToken()
        future_date = (datetime.now() + timedelta(hours=5)).strftime("%m/%d/%Y %H:%M:%S")

        result = access_token.validate_expire(future_date)

        assert result is True
        assert access_token.valid_until is not None
