"""Custom user model for the authentication system."""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from users.managers.user_manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model replacing Django's default to support username+email auth."""

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True, verbose_name="Username")
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="First Name")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Last Name")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_staff = models.BooleanField(default=False, verbose_name="Staff")
    is_superuser = models.BooleanField(default=False, verbose_name="Superuser")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.username

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
