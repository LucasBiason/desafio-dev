"""URL configuration for external microservices."""

import os


class ServiceConfig:
    """Centralizes URLs for other CNAB services, overridable via environment variables."""

    @classmethod
    def get_user_service_url(cls) -> str:
        """Returns the user-service base URL, defaulting to localhost:8001."""
        return os.environ.get("USER_SERVICE_URL", "http://127.0.0.1:8001")
