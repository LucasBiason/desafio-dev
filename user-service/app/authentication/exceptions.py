"""Custom exceptions for JWT authentication errors."""

import logging

from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)

# Constants for error messages
INVALID_TOKEN = "Invalid Token"
TOKEN_EXPIRED = "Token expired at {valid_until}"
USER_NOT_ACTIVE = "User {username} is inactive."
USER_EMAIL_REQUIRED = "Username is required."
USER_PASSWORD_REQUIRED = "Password is required."

# Constants for status codes
STATUS_FORBIDDEN = 403


class BaseAPIException(APIException):
    """Base exception that logs the error and sets the response detail and status code."""

    def __init__(self, detail: str, status_code: int = STATUS_FORBIDDEN, **kwargs) -> None:
        self.detail = detail.format(**kwargs) if kwargs else detail
        self.status_code = status_code
        logger.error("%s", self.detail)
        super().__init__(self.detail)


class InvalidTokenException(BaseAPIException):
    """Exception raised when a JWT token is invalid."""

    def __init__(self, details: str = None) -> None:
        super().__init__(detail=INVALID_TOKEN if not details else details)


class TokenExpiredException(BaseAPIException):
    """Exception raised when a JWT token has expired."""

    def __init__(self, valid_until: str = "") -> None:
        super().__init__(f"Token expired at {valid_until}")
        self.valid_until = valid_until


class UserNotActiveException(BaseAPIException):
    """Exception raised when a user is inactive."""

    def __init__(self, username: str = "") -> None:
        super().__init__(detail=USER_NOT_ACTIVE, username=username)


class UserEmailRequiredException(BaseAPIException):
    """Exception raised when the username is required but not provided."""

    def __init__(self) -> None:
        super().__init__(detail=USER_EMAIL_REQUIRED)


class UserPasswordRequiredException(BaseAPIException):
    """Exception raised when the password is required but not provided."""

    def __init__(self) -> None:
        super().__init__(detail=USER_PASSWORD_REQUIRED)
