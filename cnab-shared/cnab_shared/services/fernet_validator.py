"""Fernet token validation for service-to-service authentication."""

import json
import logging
import os
from datetime import UTC, datetime

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException

logger = logging.getLogger(__name__)

_MAX_TOKEN_AGE_SECONDS = 300  # 5 minutes


class FernetValidator:
    """Decrypts and validates Fernet tokens issued by trusted internal services."""

    def __init__(self) -> None:
        secret_key = os.environ.get("SERVICE_SECRET_KEY", "")
        self._fernet = Fernet(secret_key.encode()) if secret_key else None

    def validate_token(self, token: str) -> dict:
        """Decrypts the Fernet token, verifies its age, and returns the payload.

        Raises HTTPException 401 when the token is missing, malformed, expired,
        or the service secret key is not configured.
        """
        if self._fernet is None:
            logger.error("SERVICE_SECRET_KEY is not configured.")
            raise HTTPException(status_code=401, detail="Service authentication not configured.")

        try:
            raw = self._fernet.decrypt(token.encode())
        except InvalidToken:
            raise HTTPException(status_code=401, detail="Invalid or tampered service token.")
        except Exception as exc:
            logger.error("Fernet decryption error: %s", exc)
            raise HTTPException(status_code=401, detail="Service token decryption failed.")

        try:
            payload = json.loads(raw.decode())
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.error("Fernet token payload is not valid JSON: %s", exc)
            raise HTTPException(status_code=401, detail="Malformed service token payload.")

        timestamp_str = payload.get("timestamp")
        if not timestamp_str:
            raise HTTPException(status_code=401, detail="Service token missing timestamp.")

        try:
            issued_at = datetime.fromisoformat(timestamp_str)
        except ValueError:
            raise HTTPException(status_code=401, detail="Service token has invalid timestamp format.")

        if issued_at.tzinfo is None:
            issued_at = issued_at.replace(tzinfo=UTC)

        age_seconds = (datetime.now(tz=UTC) - issued_at).total_seconds()
        if age_seconds > _MAX_TOKEN_AGE_SECONDS:
            raise HTTPException(status_code=401, detail="Service token has expired.")

        return payload
