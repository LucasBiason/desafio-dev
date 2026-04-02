"""Serializer for the User model."""

from rest_framework import serializers

from users.models.user import User


class UserSerializer(serializers.ModelSerializer):
    """User fields for create/update/read. Password is write-only."""

    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_active",
            "is_staff",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
