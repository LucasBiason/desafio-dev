"""Shared routers module for CNAB microservices."""

from .health_router import create_health_router, health_router

__all__ = ["create_health_router", "health_router"]
