"""Custom exceptions for the Users app."""

import logging

from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class UserNotFoundException(APIException):
    """Raised when a requested user does not exist."""

    status_code = 404

    def __init__(self, user_pk: int) -> None:
        detail = f"User with id {user_pk} not found."
        self.detail = detail
        logger.error("%s", detail)
        super().__init__(detail)


class UnauthorizedUserException(APIException):
    """Raised when the authenticated user lacks permission for the requested action."""

    status_code = 403

    def __init__(self) -> None:
        detail = "You do not have permission to perform this action."
        self.detail = detail
        logger.error("%s", detail)
        super().__init__(detail)


class InvalidUserDataException(APIException):
    """Raised when user data fails a uniqueness or business rule check."""

    status_code = 400

    def __init__(self, detail: str) -> None:
        self.detail = detail
        logger.error("%s", detail)
        super().__init__(detail)
