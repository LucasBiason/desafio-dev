"""JWT access token encoding and validation."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

from authentication import exceptions

logger = logging.getLogger(__name__)


class AccessToken:
    """Encodes, decodes and validates JWT tokens."""

    def __init__(self) -> None:
        self.valid_until: Optional[datetime] = None
        self.validate_dt: bool = False
        self.encoded_token: str = ""
        self.decoded_token: Dict = {}

    def encode(self, user_id: str) -> Tuple[str, str]:
        """Return (encoded_token, expiration_string) for the given user ID."""
        expire_hours = getattr(settings, "LOGIN_EXPIRE", 5)
        valid_dt = datetime.now() + timedelta(hours=expire_hours)
        validate = valid_dt.strftime("%m/%d/%Y %H:%M:%S")
        jwt_secret = settings.SECRET_KEY
        encoded_token = jwt.encode(
            {"user": str(user_id), "validate": validate},
            jwt_secret,
            algorithm="HS256",
        )
        logger.debug("[AccessToken] Token encoded successfully.")
        return encoded_token, validate

    def decode_token(self, encoded_token: str) -> Dict:
        """Decode and return the token payload. Raises InvalidTokenException on failure."""
        try:
            logger.debug("[AccessToken] Decoding token...")
            jwt_secret = settings.SECRET_KEY
            return jwt.decode(encoded_token, key=jwt_secret, algorithms=["HS256"])
        except jwt.DecodeError as exc:
            logger.error("[AccessToken] Error decoding token.")
            raise exceptions.InvalidTokenException() from exc

    def validate_expire(self, to_validate: str) -> bool:
        """Check the token expiration date string. Raises TokenExpiredException if past due."""
        try:
            logger.debug("[AccessToken] Validating expiration date...")
            self.valid_until = datetime.strptime(to_validate, "%m/%d/%Y %H:%M:%S")
            if self.valid_until <= datetime.now():
                raise exceptions.TokenExpiredException(
                    valid_until=self.valid_until
                ) from None
            return True
        except ValueError as e:
            logger.error("[AccessToken] Invalid expiration date format: %s", e)
            raise exceptions.InvalidTokenException()

    def validate(self, token: str) -> Dict:
        """Parse, decode, and validate the Authorization header token. Returns the payload."""
        self.encoded_token = self._validate_token_format(token)
        self.decoded_token = self.decode_token(self.encoded_token)
        self.validate_dt = self.validate_expire(self.decoded_token["validate"])
        return self.decoded_token

    def _validate_token_format(self, token: str) -> str:
        """Strip and validate the Bearer prefix. Returns the raw encoded token."""
        if not token or " " not in token:
            raise AuthenticationFailed("Invalid Authorization header format.")
        prefix, encoded_token = token.split(" ", 1)
        if prefix.lower() != "bearer":
            raise AuthenticationFailed("Invalid token prefix.")
        return encoded_token
