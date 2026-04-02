"""UserManager tests."""

import pytest

from users.models.user import User


@pytest.mark.django_db
class TestUserManager:
    """User creation manager."""

    def test_create_user_success(self) -> None:
        """Creates a user with correct defaults."""
        user = User.objects.create_user(
            username="usuarionovo",
            email="usuario@example.com",
            password="senha12345",
        )

        assert user.pk is not None
        assert user.username == "usuarionovo"
        assert user.email == "usuario@example.com"
        assert user.check_password("senha12345")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_normalizes_email(self) -> None:
        """Email domain is lowercased on save."""
        user = User.objects.create_user(
            username="usuarioemail",
            email="Usuario@Example.COM",
            password="senha12345",
        )

        assert user.email == "Usuario@example.com"

    def test_create_user_without_username_raises(self) -> None:
        """Blank username raises ValueError."""
        with pytest.raises(ValueError, match="username"):
            User.objects.create_user(username="", email="email@example.com", password="senha")

    def test_create_user_without_email_raises(self) -> None:
        """Blank email raises ValueError."""
        with pytest.raises(ValueError, match="email"):
            User.objects.create_user(username="usuario", email="", password="senha")

    def test_create_superuser_success(self) -> None:
        """Superuser has is_staff and is_superuser set to True."""
        superuser = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="admin12345",
        )

        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.is_active is True

    def test_create_superuser_is_staff_false_raises(self) -> None:
        """is_staff=False on superuser raises ValueError."""
        with pytest.raises(ValueError, match="is_staff"):
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin12345",
                is_staff=False,
            )

    def test_create_superuser_is_superuser_false_raises(self) -> None:
        """is_superuser=False on superuser raises ValueError."""
        with pytest.raises(ValueError, match="is_superuser"):
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin12345",
                is_superuser=False,
            )
