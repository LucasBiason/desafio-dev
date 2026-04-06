"""User management API view tests."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from users.models.user import User

factory = APIRequestFactory()


@pytest.mark.django_db
class TestCreateUser:
    """POST /users/v1/users/."""

    def test_create_user_as_staff(self, authenticated_client: APIClient, create_user: User) -> None:
        """Staff user creates another user successfully."""
        create_user.is_staff = True
        create_user.save()

        response = authenticated_client.post(
            "/users/v1/users/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "newpass123",
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["username"] == "newuser"
        assert response.json()["email"] == "new@example.com"

    def test_create_user_as_superuser(self, api_client: APIClient) -> None:
        """Superuser creates a user successfully."""
        superuser = User.objects.create_superuser(username="admin", email="admin@example.com", password="admin123")
        from authentication.services.access_token import AccessToken

        token, _ = AccessToken().encode(str(superuser.id))
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.post(
            "/users/v1/users/",
            {
                "username": "created_by_admin",
                "email": "created@example.com",
                "password": "pass123",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_user_unauthorized(self, authenticated_client: APIClient) -> None:
        """Regular user creating another account returns 403."""
        response = authenticated_client.post(
            "/users/v1/users/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "newpass123",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_user_duplicate_username(self, authenticated_client: APIClient, create_user: User) -> None:
        """Duplicate username returns 400."""
        create_user.is_staff = True
        create_user.save()

        response = authenticated_client.post(
            "/users/v1/users/",
            {
                "username": "testuser",
                "email": "other@example.com",
                "password": "newpass123",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_no_auth(self, api_client: APIClient) -> None:
        """Unauthenticated request returns 403."""
        response = api_client.post(
            "/users/v1/users/",
            {"username": "newuser", "email": "new@example.com", "password": "pass"},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestListUsers:
    """GET /users/v1/users/."""

    def test_list_users_paginated(self, authenticated_client: APIClient) -> None:
        """Returns paginated response with count, next, previous, results."""
        response = authenticated_client.get("/users/v1/users/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data
        assert "results" in data
        assert "next" in data
        assert "previous" in data
        assert len(data["results"]) >= 1

    def test_list_users_no_pagination_fallback(self, authenticated_client: APIClient) -> None:
        """No pagination class returns a flat list."""
        from unittest.mock import patch

        with patch.object(
            type(authenticated_client),
            "get",
            wraps=authenticated_client.get,
        ):
            # Force paginate_queryset to return None by removing pagination class
            from users.views.user import ManageUserView

            original = ManageUserView.pagination_class
            ManageUserView.pagination_class = None
            try:
                response = authenticated_client.get("/users/v1/users/")
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert isinstance(data, list)
            finally:
                ManageUserView.pagination_class = original

    def test_list_users_no_auth(self, api_client: APIClient) -> None:
        """Unauthenticated request returns 403."""
        response = api_client.get("/users/v1/users/")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestRetrieveUser:
    """GET /users/v1/users/{id}/."""

    def test_retrieve_own_user(self, authenticated_client: APIClient, create_user: User) -> None:
        """Returns own user data."""
        response = authenticated_client.get(f"/users/v1/users/{create_user.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == "testuser"

    def test_retrieve_nonexistent_user(self, authenticated_client: APIClient) -> None:
        """Nonexistent user returns 404."""
        response = authenticated_client.get("/users/v1/users/99999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUpdateUser:
    """PATCH /users/v1/users/{id}/."""

    def test_update_own_user(self, authenticated_client: APIClient, create_user: User) -> None:
        """Own user data is updated successfully."""
        response = authenticated_client.patch(
            f"/users/v1/users/{create_user.id}/",
            {"first_name": "Updated"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["first_name"] == "Updated"


@pytest.mark.django_db
class TestDestroyUser:
    """DELETE /users/v1/users/{id}/."""

    def test_destroy_as_staff(self, api_client: APIClient) -> None:
        """Staff soft-deletes a user by setting is_active to False."""
        staff = User.objects.create_user(username="staff", email="staff@example.com", password="pass123", is_staff=True)
        target = User.objects.create_user(username="target", email="target@example.com", password="pass123")
        from authentication.services.access_token import AccessToken

        token, _ = AccessToken().encode(str(staff.id))
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.delete(f"/users/v1/users/{target.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        target.refresh_from_db()
        assert target.is_active is False

    def test_destroy_superuser_blocked_by_regular_staff(self, api_client: APIClient) -> None:
        """Staff deleting a superuser returns 403."""
        staff = User.objects.create_user(
            username="staffblocked",
            email="staffblocked@example.com",
            password="pass123",
            is_staff=True,
        )
        superuser = User.objects.create_superuser(
            username="superprotected",
            email="superprotected@example.com",
            password="admin123",
        )
        from authentication.services.access_token import AccessToken

        token, _ = AccessToken().encode(str(staff.id))
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.delete(f"/users/v1/users/{superuser.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestGetQueryset:
    """ManageUserView.get_queryset()."""

    def test_get_queryset_returns_users(self, create_user: User, auth_token: str) -> None:
        """Returns a queryset containing the existing test user."""
        from users.views.user import ManageUserView

        request = factory.get("/users/v1/users/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {auth_token}"

        view = ManageUserView()
        view.request = request
        view.kwargs = {}
        view.format_kwarg = None

        queryset = view.get_queryset()

        assert queryset is not None
        usernames = [u.username for u in queryset]
        assert "testuser" in usernames


@pytest.mark.django_db
class TestUpdateUserEndpoint:
    """PUT/PATCH username and email validation."""

    def test_update_user_with_new_username_and_email(self, authenticated_client: APIClient, create_user: User) -> None:
        """Non-conflicting username and email are updated successfully."""
        response = authenticated_client.patch(
            f"/users/v1/users/{create_user.id}/",
            {"username": "updatedusername", "email": "updated@example.com"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == "updatedusername"
        assert response.json()["email"] == "updated@example.com"
