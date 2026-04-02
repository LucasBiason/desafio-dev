"""Configuration for the authentication app."""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """App config for the authentication module."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
    verbose_name = "Authentication"
