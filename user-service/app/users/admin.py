"""Admin panel configuration for the users app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models.user import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom user model.

    Displays the most relevant fields in the list view and allows search and
    filtering by common fields, making user management easier in the Django panel.
    """

    list_display = ["id", "username", "email", "first_name", "last_name", "is_active", "is_staff", "created_at"]
    search_fields = ["username", "email", "first_name", "last_name"]
    list_filter = ["is_active", "is_staff", "is_superuser"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Information", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    readonly_fields = ["created_at", "updated_at"]

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )
