"""User model tests."""

import pytest

from users.models.user import User


@pytest.mark.django_db
class TestUserStr:
    """User.__str__."""

    def test_str_returns_username(self) -> None:
        """str(user) returns the username."""
        user = User.objects.create_user(
            username="struser",
            email="struser@example.com",
            password="pass123",
        )

        assert str(user) == "struser"


@pytest.mark.django_db
class TestUserGetFullName:
    """User.get_full_name."""

    def test_get_full_name_with_both_names(self) -> None:
        """Returns 'First Last' when both names are set."""
        user = User.objects.create_user(
            username="fullnameuser",
            email="fullname@example.com",
            password="pass123",
            first_name="John",
            last_name="Doe",
        )

        assert user.get_full_name() == "John Doe"

    def test_get_full_name_with_only_first_name(self) -> None:
        """Returns first name only when last_name is blank."""
        user = User.objects.create_user(
            username="firstonly",
            email="firstonly@example.com",
            password="pass123",
            first_name="Alice",
            last_name="",
        )

        assert user.get_full_name() == "Alice"

    def test_get_full_name_with_no_names(self) -> None:
        """Returns empty string when both names are blank."""
        user = User.objects.create_user(
            username="nonames",
            email="nonames@example.com",
            password="pass123",
        )

        assert user.get_full_name() == ""
