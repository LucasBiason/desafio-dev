"""Core views module."""

from .health import health_view
from .swagger import schema_view

__all__ = ["health_view", "schema_view"]
