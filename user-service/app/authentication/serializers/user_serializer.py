"""Serializer for the user model."""

from rest_framework import serializers

from users.models.user import User


class UserSerializer(serializers.ModelSerializer):
    """Public user fields for authentication responses (no password)."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
