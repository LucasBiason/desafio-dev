"""Tests for require_service_token dependency."""

import json
import os
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet
from fastapi import HTTPException

_TEST_KEY = Fernet.generate_key()


def _make_valid_token(key: bytes = _TEST_KEY) -> str:
    """Creates a fresh valid Fernet token."""
    fernet = Fernet(key)
    payload = json.dumps(
        {"service": "upload-service", "timestamp": datetime.now(tz=UTC).isoformat()}
    ).encode()
    return fernet.encrypt(payload).decode()


class TestRequireServiceToken:
    """Tests for the require_service_token FastAPI dependency."""

    def test_valid_token_returns_payload(self):
        """require_service_token returns the decrypted payload for a valid token."""
        from app.validators.fernet_middleware import require_service_token

        with patch.dict(os.environ, {"SERVICE_SECRET_KEY": _TEST_KEY.decode()}):
            payload = require_service_token(x_service_token=_make_valid_token())

        assert "service" in payload

    def test_invalid_token_raises_401(self):
        """require_service_token raises HTTPException 401 for invalid tokens."""
        from app.validators.fernet_middleware import require_service_token

        with patch.dict(os.environ, {"SERVICE_SECRET_KEY": _TEST_KEY.decode()}):
            with pytest.raises(HTTPException) as exc_info:
                require_service_token(x_service_token="invalid-garbage")

        assert exc_info.value.status_code == 401
