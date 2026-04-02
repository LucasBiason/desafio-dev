"""Serializer for the login response."""

from rest_framework import serializers

from authentication.serializers.user_serializer import UserSerializer


class LoginSerializer(serializers.Serializer):
    """Login response: JWT token and user data."""

    encoded_token = serializers.CharField(
        help_text="Token containing the information needed to authenticate on other services."
    )
    user = UserSerializer()
