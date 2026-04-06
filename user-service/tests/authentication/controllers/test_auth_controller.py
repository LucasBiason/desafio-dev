"""JWTAuthentication controller tests."""

import pytest
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory

from authentication.controllers.auth_controller import JWTAuthentication
from authentication.exceptions import UserNotActiveException
from users.models.user import User

factory = APIRequestFactory()


@pytest.mark.django_db
class TestJWTAuthenticationLogin:
    """JWTAuthentication.login()."""

    def test_login_success(self) -> None:
        """Should return encoded_token and user data."""
        User.objects.create_user(username="authuser", email="auth@example.com", password="authpass123")
        request = factory.post("/auth/v1/login/")
        request.data = {"username": "authuser", "password": "authpass123"}

        result = JWTAuthentication.login(request)

        assert "encoded_token" in result
        assert "valid_until" in result
        assert result["user"]["username"] == "authuser"

    def test_login_wrong_password(self) -> None:
        """Should raise AuthenticationFailed on wrong password."""
        User.objects.create_user(username="authuser2", email="auth2@example.com", password="authpass123")
        request = factory.post("/auth/v1/login/")
        request.data = {"username": "authuser2", "password": "wrongpass"}

        with pytest.raises(AuthenticationFailed):
            JWTAuthentication.login(request)

    def test_login_missing_username(self) -> None:
        """Should raise exception when username is missing."""
        from authentication.exceptions import UserEmailRequiredException

        request = factory.post("/auth/v1/login/")
        request.data = {"password": "testpass123"}

        with pytest.raises(UserEmailRequiredException):
            JWTAuthentication.login(request)


@pytest.mark.django_db
class TestJWTAuthenticationValidate:
    """JWTAuthentication.validate()."""

    def test_validate_success(self, create_user: User, auth_token: str) -> None:
        """Should return user data on valid token."""
        request = factory.post("/auth/v1/validate/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {auth_token}"

        result = JWTAuthentication.validate(request)

        assert result["user"]["username"] == "testuser"
        assert "encoded_token" in result

    def test_validate_return_user(self, create_user: User, auth_token: str) -> None:
        """Should return user instance when return_user=True."""
        request = factory.post("/auth/v1/validate/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {auth_token}"

        user = JWTAuthentication.validate(request, return_user=True)

        assert isinstance(user, User)
        assert user.username == "testuser"

    def test_validate_inactive_user(self, create_user: User, auth_token: str) -> None:
        """Should raise UserNotActiveException on inactive user."""
        create_user.is_active = False
        create_user.save()

        request = factory.post("/auth/v1/validate/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {auth_token}"

        with pytest.raises(UserNotActiveException):
            JWTAuthentication.validate(request)


@pytest.mark.django_db
class TestJWTAuthenticationAuthenticate:
    """JWTAuthentication.authenticate() instance method."""

    def test_authenticate_success(self, create_user: User, auth_token: str) -> None:
        """Should return (user, token_data) tuple on a valid token."""
        request = factory.get("/users/v1/users/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {auth_token}"

        auth = JWTAuthentication()
        result = auth.authenticate(request)

        assert result is not None
        user_obj, token_data = result
        assert isinstance(user_obj, User)
        assert user_obj.username == "testuser"
        assert token_data["user"] == str(create_user.id)

    def test_authenticate_inactive_user_raises(self, create_user: User, auth_token: str) -> None:
        """Should raise UserNotActiveException when the authenticated user is inactive."""
        create_user.is_active = False
        create_user.save()

        request = factory.get("/users/v1/users/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {auth_token}"

        auth = JWTAuthentication()

        with pytest.raises(UserNotActiveException):
            auth.authenticate(request)


@pytest.mark.django_db
class TestJWTAuthenticationLoginInactiveAfterAuth:
    """Inactive user path in JWTAuthentication.login() after Django authenticate."""

    def test_login_inactive_user_raises(self) -> None:
        """Inactive user raises UserNotActiveException even when Django authenticate returns the user."""
        from unittest.mock import patch

        user = User.objects.create_user(
            username="manualinactive",
            email="manualinactive@example.com",
            password="pass123",
            is_active=True,
        )
        user.is_active = False

        request = factory.post("/auth/v1/login/")
        request.data = {"username": "manualinactive", "password": "pass123"}

        with patch(
            "authentication.controllers.auth_controller.authenticate",
            return_value=user,
        ):
            with pytest.raises(UserNotActiveException):
                JWTAuthentication.login(request)
