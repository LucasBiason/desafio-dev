"""Shared fixtures for the test suite."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.test_settings")

import django

django.setup()

import pytest
from rest_framework.test import APIClient

from users.models.user import User


@pytest.fixture
def api_client() -> APIClient:
    """Unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user_data() -> dict:
    """Default user payload."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def create_user(user_data: dict) -> User:
    """Persisted test user."""
    user = User.objects.create_user(**user_data)
    return user


@pytest.fixture
def auth_token(create_user: User) -> str:
    """Valid JWT token for the test user."""
    from authentication.services.access_token import AccessToken

    token, _ = AccessToken().encode(str(create_user.id))
    return token


@pytest.fixture
def authenticated_client(api_client: APIClient, auth_token: str) -> APIClient:
    """API client pre-loaded with a valid Bearer token."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
    return api_client
