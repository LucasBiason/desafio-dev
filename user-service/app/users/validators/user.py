"""Validator for user operations."""

from users.validators.exceptions import (
    InvalidUserDataException,
    UnauthorizedUserException,
    UserNotFoundException,
)


class UserValidator:
    """Authorization and uniqueness checks for user operations."""

    def __init__(self, logged_user, user_repository) -> None:
        self.logged_user = logged_user
        self.user_repository = user_repository

    def validate_user_access(self, user_pk: int) -> None:
        """Check that the logged user can access the target user.

        Superusers can access anyone. Staff can access non-superusers.
        Regular users can only access themselves.
        """
        target_user = self.user_repository.retrieve(user_pk)
        if target_user is None:
            raise UserNotFoundException(user_pk)

        if self.logged_user.is_superuser:
            return

        if self.logged_user.is_staff:
            if target_user.is_superuser:
                raise UnauthorizedUserException()
            return

        if self.logged_user.pk != target_user.pk:
            raise UnauthorizedUserException()

    def can_create_user(self) -> None:
        """Raise UnauthorizedUserException if the logged user is not staff or superuser."""
        if not (self.logged_user.is_superuser or self.logged_user.is_staff):
            raise UnauthorizedUserException()

    def validate_username(self, username: str, user_id: int | None = None) -> None:
        """Raise InvalidUserDataException if the username is already taken."""
        existing = self.user_repository.retrieve_by_username(username, exclude_user_id=user_id)
        if existing is not None:
            raise InvalidUserDataException(f"The username '{username}' is already in use.")

    def validate_email(self, email: str, user_id: int | None = None) -> None:
        """Raise InvalidUserDataException if the email is already registered."""
        existing = self.user_repository.retrieve_by_email(email, exclude_user_id=user_id)
        if existing is not None:
            raise InvalidUserDataException(f"The email '{email}' is already registered.")
