"""JWT-based authentication: login, token validation, and DRF authenticate hook."""

import logging
from typing import Dict, Optional, Tuple

from django.contrib.auth import authenticate
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from authentication.services.access_token import AccessToken
from authentication.exceptions import (
    UserEmailRequiredException,
    UserNotActiveException,
    UserPasswordRequiredException,
)
from authentication.serializers import UserSerializer
from users.models.user import User

logger = logging.getLogger(__name__)


class JWTAuthentication(BaseAuthentication):
    """DRF authentication backend for JWT tokens."""

    @staticmethod
    def login(request) -> Dict:
        """Authenticate credentials and return a JWT token with user data."""
        username = request.data.get("username")
        password = request.data.get("password")

        if not username:
            raise UserEmailRequiredException()
        if not password:
            raise UserPasswordRequiredException()

        user = authenticate(request, username=username, password=password)

        if not user:
            raise AuthenticationFailed(
                "Unable to authenticate with provided credentials."
            )

        if not user.is_active:
            raise UserNotActiveException(user.username)

        encoded_token, validate = AccessToken().encode(str(user.id))
        user_data = UserSerializer(user).data

        return {
            "encoded_token": encoded_token,
            "valid_until": validate,
            "user": user_data,
        }

    @staticmethod
    def validate(request, return_user: bool = False):
        """Validate the Authorization header token and return user data or the User instance."""
        token = request.headers.get("Authorization", "")

        access_token = AccessToken()
        token_data = access_token.validate(token)

        user = User.objects.get(pk=token_data["user"])
        if not user.is_active:
            raise UserNotActiveException(user.username)

        if return_user:
            return user

        user_data = UserSerializer(user).data

        return {
            "encoded_token": access_token.encoded_token,
            "valid_until": access_token.valid_until,
            "user": user_data,
        }

    def authenticate(self, request) -> Tuple[Optional[object], Optional[Dict]]:
        """DRF authenticate hook — returns (user, token_data) from the Authorization header."""
        token = request.headers.get("Authorization", "")
        token_data = AccessToken().validate(token)

        user = User.objects.get(pk=token_data["user"])
        if not user.is_active:
            raise UserNotActiveException(user.username)

        return user, token_data
