"""Database connection configuration."""

import os


class DatabaseConfig:
    """Reads environment variables for the PostgreSQL database connection."""

    @classmethod
    def get_database_url(cls) -> str | None:
        """Returns the DATABASE_URL environment variable, or None if not set."""
        return os.environ.get("DATABASE_URL")
