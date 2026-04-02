"""Controller for user business logic."""

from django.db import transaction

from users.models.user import User
from users.repositories.user import UserRepository
from users.validators.user import UserValidator


class UserController:
    """Coordinates user CRUD operations between the repository and validator."""

    def __init__(self, logged_user: User) -> None:
        self.logged_user = logged_user
        self.repository = UserRepository()
        self.validator = UserValidator(logged_user, self.repository)

    def retrieve(self, user_pk: int) -> User:
        """Retrieve a user by PK after validating access permissions."""
        self.validator.validate_user_access(user_pk)
        return self.repository.retrieve(user_pk)

    def list_users(self, filters: dict | None = None) -> list[User]:
        """Return a queryset of users, optionally filtered by the given parameters."""
        kwargs = filters or {}
        return self.repository.queryset(**kwargs)

    @transaction.atomic
    def create_user(self, data: dict) -> User:
        """Create a new user after checking permissions and field uniqueness."""
        self.validator.can_create_user()

        username = data.get("username")
        email = data.get("email")

        if username:
            self.validator.validate_username(username)
        if email:
            self.validator.validate_email(email)

        return self.repository.save(data)

    @transaction.atomic
    def update_user(self, user_pk: int, data: dict) -> User:
        """Update a user after validating access and field uniqueness."""
        self.validator.validate_user_access(user_pk)
        user = self.repository.retrieve(user_pk)

        username = data.get("username")
        email = data.get("email")

        if username:
            self.validator.validate_username(username, user_id=user_pk)
        if email:
            self.validator.validate_email(email, user_id=user_pk)

        return self.repository.save(data, user=user)

    @transaction.atomic
    def destroy_user(self, user_pk: int) -> User:
        """Soft-delete a user by setting is_active to False."""
        self.validator.validate_user_access(user_pk)
        user = self.repository.retrieve(user_pk)
        return self.repository.destroy(user)
