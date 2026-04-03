"""Tests for FernetValidator service."""

import json
import os
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet
from fastapi import HTTPException

from app.services.fernet_validator import FernetValidator

_TEST_KEY = Fernet.generate_key()


def _make_token(payload: dict, key: bytes = _TEST_KEY) -> str:
    """Creates a valid Fernet token from the given payload."""
    fernet = Fernet(key)
    raw = json.dumps(payload).encode()
    return fernet.encrypt(raw).decode()


def _fresh_payload() -> dict:
    """Returns a payload with a current timestamp."""
    return {
        "service": "upload-service",
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }


class TestFernetValidator:
    """Tests for FernetValidator token validation logic."""

    def _make_validator(self, key: bytes = _TEST_KEY) -> FernetValidator:
        """Creates a FernetValidator with the given secret key in the environment."""
        with patch.dict(os.environ, {"SERVICE_SECRET_KEY": key.decode()}):
            return FernetValidator()

    def test_valid_token_returns_payload(self):
        """validate_token returns the payload dict for a valid, fresh token."""
        validator = self._make_validator()
        token = _make_token(_fresh_payload())
        payload = validator.validate_token(token)
        assert payload["service"] == "upload-service"

    def test_expired_token_raises_401(self):
        """validate_token raises HTTPException 401 for tokens older than 5 minutes."""
        validator = self._make_validator()
        old_ts = (datetime.now(tz=UTC) - timedelta(minutes=10)).isoformat()
        token = _make_token({"service": "upload-service", "timestamp": old_ts})
        with pytest.raises(HTTPException) as exc_info:
            validator.validate_token(token)
        assert exc_info.value.status_code == 401

    def test_invalid_token_raises_401(self):
        """validate_token raises HTTPException 401 for a tampered/invalid token."""
        validator = self._make_validator()
        with pytest.raises(HTTPException) as exc_info:
            validator.validate_token("not-a-valid-fernet-token")
        assert exc_info.value.status_code == 401

    def test_missing_timestamp_raises_401(self):
        """validate_token raises HTTPException 401 when timestamp is absent."""
        validator = self._make_validator()
        token = _make_token({"service": "upload-service"})
        with pytest.raises(HTTPException) as exc_info:
            validator.validate_token(token)
        assert exc_info.value.status_code == 401

    def test_invalid_timestamp_format_raises_401(self):
        """validate_token raises HTTPException 401 for non-ISO timestamp."""
        validator = self._make_validator()
        token = _make_token({"service": "upload-service", "timestamp": "not-a-date"})
        with pytest.raises(HTTPException) as exc_info:
            validator.validate_token(token)
        assert exc_info.value.status_code == 401

    def test_missing_key_raises_401(self):
        """validate_token raises HTTPException 401 when SERVICE_SECRET_KEY is not set."""
        with patch.dict(os.environ, {"SERVICE_SECRET_KEY": ""}):
            validator = FernetValidator()
        with pytest.raises(HTTPException) as exc_info:
            validator.validate_token("any-token")
        assert exc_info.value.status_code == 401

    def test_wrong_key_raises_401(self):
        """validate_token raises HTTPException 401 when token was encrypted with a different key."""
        other_key = Fernet.generate_key()
        token = _make_token(_fresh_payload(), key=other_key)
        validator = self._make_validator(key=_TEST_KEY)
        with pytest.raises(HTTPException) as exc_info:
            validator.validate_token(token)
        assert exc_info.value.status_code == 401

    def test_token_at_boundary_is_valid(self):
        """validate_token accepts tokens issued exactly 4 minutes and 59 seconds ago."""
        validator = self._make_validator()
        recent_ts = (datetime.now(tz=UTC) - timedelta(seconds=299)).isoformat()
        token = _make_token({"service": "upload-service", "timestamp": recent_ts})
        payload = validator.validate_token(token)
        assert "service" in payload

    def test_non_json_payload_raises_401(self):
        """validate_token raises HTTPException 401 when payload is not JSON."""
        fernet = Fernet(_TEST_KEY)
        raw_token = fernet.encrypt(b"not-json").decode()
        validator = self._make_validator()
        with pytest.raises(HTTPException) as exc_info:
            validator.validate_token(raw_token)
        assert exc_info.value.status_code == 401

    def test_generic_decryption_exception_raises_401(self):
        """validate_token raises HTTPException 401 for unexpected decryption errors."""
        from unittest.mock import patch as _patch

        validator = self._make_validator()
        with _patch.object(validator._fernet, "decrypt", side_effect=RuntimeError("unexpected")):
            with pytest.raises(HTTPException) as exc_info:
                validator.validate_token("any-token")
        assert exc_info.value.status_code == 401

    def test_timezone_naive_timestamp_is_accepted(self):
        """validate_token handles timezone-naive ISO timestamps by treating them as UTC."""
        from datetime import datetime

        validator = self._make_validator()
        # Use a naive timestamp far in the future to avoid expiry checks.
        future_ts = datetime(2099, 1, 1, 12, 0, 0).isoformat()
        token = _make_token({"service": "upload-service", "timestamp": future_ts})
        # The token will not be expired since future_ts is in the future,
        # and age_seconds will be negative (well under _MAX_TOKEN_AGE_SECONDS).
        payload = validator.validate_token(token)
        assert "service" in payload
