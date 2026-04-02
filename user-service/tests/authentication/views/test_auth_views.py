"""Auth API view tests."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from users.models.user import User


@pytest.mark.django_db
class TestLogin:
    """POST /auth/v1/login/."""

    def test_login_success(self, api_client: APIClient, create_user: User) -> None:
        """Valid credentials return token and user data."""
        response = api_client.post(
            "/auth/v1/login/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "encoded_token" in response.json()
        assert "valid_until" in response.json()
        assert response.json()["user"]["username"] == "testuser"

    def test_login_invalid_password(self, api_client: APIClient, create_user: User) -> None:
        """Wrong password returns 403."""
        response = api_client.post(
            "/auth/v1/login/",
            {"username": "testuser", "password": "wrongpass"},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_login_nonexistent_user(self, api_client: APIClient) -> None:
        """Unknown user returns 403."""
        response = api_client.post(
            "/auth/v1/login/",
            {"username": "noone", "password": "testpass123"},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_login_missing_username(self, api_client: APIClient) -> None:
        """Missing username returns 403."""
        response = api_client.post(
            "/auth/v1/login/",
            {"password": "testpass123"},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_login_missing_password(self, api_client: APIClient) -> None:
        """Missing password returns 403."""
        response = api_client.post(
            "/auth/v1/login/",
            {"username": "testuser"},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_login_inactive_user(self, api_client: APIClient) -> None:
        """Inactive user returns 403."""
        user = User.objects.create_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="testpass123",
        )
        user.is_active = False
        user.save()

        response = api_client.post(
            "/auth/v1/login/",
            {"username": "inactiveuser", "password": "testpass123"},
            format="json",
        )

        # Django's authenticate() returns None for inactive users
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestValidator:
    """POST /auth/v1/validate/."""

    def test_validate_valid_token(self, authenticated_client: APIClient) -> None:
        """Valid token returns user data."""
        response = authenticated_client.post("/auth/v1/validate/")

        assert response.status_code == status.HTTP_200_OK
        assert "encoded_token" in response.json()
        assert "valid_until" in response.json()
        assert response.json()["user"]["username"] == "testuser"

    def test_validate_invalid_token(self, api_client: APIClient) -> None:
        """Invalid token returns 403."""
        api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.here")
        response = api_client.post("/auth/v1/validate/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_validate_missing_token(self, api_client: APIClient) -> None:
        """No Authorization header returns 403."""
        response = api_client.post("/auth/v1/validate/")

        assert response.status_code == status.HTTP_403_FORBIDDEN



@pytest.mark.django_db
class TestHealthCheck:
    """GET /health/."""

    def test_health_check(self, api_client: APIClient) -> None:
        """Returns 200 with service name and version."""
        response = api_client.get("/health/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["system_name"] == "user-service"
        assert response.json()["status"] == "healthy"
        assert "version" in response.json()
        assert "timestamp" in response.json()
