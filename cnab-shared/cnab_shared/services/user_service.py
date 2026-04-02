"""HTTP client for token validation against the user-service."""

import logging

import httpx

from ..config.service_config import ServiceConfig

logger = logging.getLogger(__name__)


class UserService:
    """HTTP client for the user-service authentication API."""

    def __init__(self) -> None:
        self.base_url = ServiceConfig.get_user_service_url()

    def validate_token(self, token: str) -> dict | None:
        """Validates a Bearer token against the user-service.

        Returns user data dict on success, None on invalid token.
        Raises ConnectionError if user-service is unreachable.
        """
        try:
            response = httpx.post(
                f"{self.base_url}/auth/v1/validate/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0,
            )

            if response.status_code == 200:
                return response.json()

            return None

        except httpx.RequestError as exc:
            logger.error("Error connecting to user-service: %s", exc)
            raise ConnectionError(f"User service unavailable: {exc}") from exc
