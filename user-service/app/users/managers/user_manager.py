"""Custom manager for the user model."""

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Manager for the custom User model."""

    def create_user(self, username: str, email: str, password: str | None = None, **extra_fields) -> "User":  # type: ignore[name-defined]  # noqa: F821
        """Create and save a regular user. Raises ValueError if username or email are missing."""
        if not username:
            raise ValueError("The username field is required.")
        if not email:
            raise ValueError("The email field is required.")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, email: str, password: str | None = None, **extra_fields) -> "User":  # type: ignore[name-defined]  # noqa: F821
        """Create a superuser with is_staff and is_superuser set to True."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)
