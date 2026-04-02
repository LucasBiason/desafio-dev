"""Custom exception hierarchy for CNAB microservices."""


class CNABBaseException(Exception):
    """Base exception for all CNAB custom exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int,
        detail: str | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class AuthenticationError(CNABBaseException):
    """Authentication failure (HTTP 401)."""

    def __init__(
        self,
        message: str = "Invalid authentication.",
        detail: str | None = None,
    ) -> None:
        super().__init__(message=message, status_code=401, detail=detail)


class TokenExpiredError(CNABBaseException):
    """Expired authentication token (HTTP 401)."""

    def __init__(
        self,
        message: str = "Token expired.",
        detail: str | None = None,
    ) -> None:
        super().__init__(message=message, status_code=401, detail=detail)


class MissingAuthorizationHeaderError(CNABBaseException):
    """Missing authorization header on a protected route (HTTP 401)."""

    def __init__(
        self,
        message: str = "Missing authorization header.",
        detail: str | None = None,
    ) -> None:
        super().__init__(message=message, status_code=401, detail=detail)


class ValidationError(CNABBaseException):
    """Input data validation failure (HTTP 400)."""

    def __init__(
        self,
        message: str = "Invalid data.",
        detail: str | None = None,
    ) -> None:
        super().__init__(message=message, status_code=400, detail=detail)


class PermissionDeniedError(CNABBaseException):
    """Access denied to a protected resource (HTTP 403)."""

    def __init__(
        self,
        message: str = "Permission denied.",
        detail: str | None = None,
    ) -> None:
        super().__init__(message=message, status_code=403, detail=detail)


class ResourceNotFoundError(CNABBaseException):
    """Requested resource not found (HTTP 404)."""

    def __init__(
        self,
        message: str = "Resource not found.",
        detail: str | None = None,
    ) -> None:
        super().__init__(message=message, status_code=404, detail=detail)


class DuplicateResourceError(CNABBaseException):
    """Attempted creation of a duplicate resource (HTTP 409)."""

    def __init__(
        self,
        message: str = "Resource already exists.",
        detail: str | None = None,
    ) -> None:
        super().__init__(message=message, status_code=409, detail=detail)


class DatabaseError(CNABBaseException):
    """Internal database error (HTTP 500)."""

    def __init__(
        self,
        message: str = "Internal database error.",
        detail: str | None = None,
    ) -> None:
        super().__init__(message=message, status_code=500, detail=detail)
