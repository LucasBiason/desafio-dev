"""UserValidator tests."""

import pytest

from users.models.user import User
from users.repositories.user import UserRepository
from users.validators.user import UserValidator
from users.validators.exceptions import (
    InvalidUserDataException,
    UnauthorizedUserException,
)


@pytest.fixture
def repo() -> UserRepository:
    """UserRepository instance."""
    return UserRepository()


@pytest.mark.django_db
class TestValidateUsername:
    """UserValidator.validate_username."""

    def test_validate_username_unique_passes(self, repo: UserRepository) -> None:
        """Unique username passes without raising."""
        logged_user = User.objects.create_user(
            username="validatorowner",
            email="validatorowner@example.com",
            password="pass123",
        )
        validator = UserValidator(logged_user, repo)

        validator.validate_username("brand_new_username")

    def test_validate_username_taken_raises(self, repo: UserRepository) -> None:
        """Taken username raises InvalidUserDataException."""
        existing = User.objects.create_user(
            username="taken_name",
            email="taken@example.com",
            password="pass123",
        )
        logged_user = User.objects.create_user(
            username="checker",
            email="checker@example.com",
            password="pass123",
        )
        validator = UserValidator(logged_user, repo)

        with pytest.raises(InvalidUserDataException):
            validator.validate_username("taken_name")

    def test_validate_username_excludes_own_id(self, repo: UserRepository) -> None:
        """Own username is excluded from conflict check."""
        user = User.objects.create_user(
            username="selfupdate",
            email="selfupdate@example.com",
            password="pass123",
        )
        validator = UserValidator(user, repo)

        validator.validate_username("selfupdate", user_id=user.pk)


@pytest.mark.django_db
class TestValidateEmail:
    """UserValidator.validate_email."""

    def test_validate_email_unique_passes(self, repo: UserRepository) -> None:
        """Unregistered email passes without raising."""
        logged_user = User.objects.create_user(
            username="emailchecker",
            email="emailchecker@example.com",
            password="pass123",
        )
        validator = UserValidator(logged_user, repo)

        validator.validate_email("brand.new@example.com")

    def test_validate_email_taken_raises(self, repo: UserRepository) -> None:
        """Already registered email raises InvalidUserDataException."""
        User.objects.create_user(
            username="emailowner",
            email="taken@example.com",
            password="pass123",
        )
        logged_user = User.objects.create_user(
            username="emailverifier",
            email="emailverifier@example.com",
            password="pass123",
        )
        validator = UserValidator(logged_user, repo)

        with pytest.raises(InvalidUserDataException):
            validator.validate_email("taken@example.com")


@pytest.mark.django_db
class TestValidateUserAccess:
    """UserValidator.validate_user_access."""

    def test_staff_can_access_non_superuser(self, repo: UserRepository) -> None:
        """Staff can access non-superuser accounts."""
        staff_user = User.objects.create_user(
            username="staffaccess",
            email="staffaccess@example.com",
            password="pass123",
            is_staff=True,
        )
        target = User.objects.create_user(
            username="regulartarget",
            email="regulartarget@example.com",
            password="pass123",
        )
        validator = UserValidator(staff_user, repo)

        validator.validate_user_access(target.pk)

    def test_staff_cannot_access_superuser(self, repo: UserRepository) -> None:
        """Staff accessing a superuser raises UnauthorizedUserException."""
        staff_user = User.objects.create_user(
            username="staffdenied",
            email="staffdenied@example.com",
            password="pass123",
            is_staff=True,
        )
        superuser = User.objects.create_superuser(
            username="protectedadmin",
            email="protectedadmin@example.com",
            password="admin123",
        )
        validator = UserValidator(staff_user, repo)

        with pytest.raises(UnauthorizedUserException):
            validator.validate_user_access(superuser.pk)

    def test_superuser_can_access_any_user(self, repo: UserRepository) -> None:
        """Superuser can access any account."""
        superuser = User.objects.create_superuser(
            username="adminaccess",
            email="adminaccess@example.com",
            password="admin123",
        )
        target = User.objects.create_user(
            username="sometarget",
            email="sometarget@example.com",
            password="pass123",
        )
        validator = UserValidator(superuser, repo)

        validator.validate_user_access(target.pk)

    def test_regular_user_cannot_access_another_user(self, repo: UserRepository) -> None:
        """Regular user accessing another account raises UnauthorizedUserException."""
        regular = User.objects.create_user(
            username="regularuser",
            email="regularuser@example.com",
            password="pass123",
        )
        other = User.objects.create_user(
            username="otheruserx",
            email="otheruserx@example.com",
            password="pass123",
        )
        validator = UserValidator(regular, repo)

        with pytest.raises(UnauthorizedUserException):
            validator.validate_user_access(other.pk)
