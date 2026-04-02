"""API endpoint for token validation."""

import logging
from typing import Dict

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication import schemas
from authentication.controllers.auth_controller import JWTAuthentication

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class Validator(APIView):
    """POST /validate — verify a JWT token and return the associated user data."""

    permission_classes = []
    authentication_classes = []

    @schemas.validate
    def post(self, request) -> Response:
        logged_user: Dict = JWTAuthentication.validate(request)
        return Response(logged_user, status=status.HTTP_200_OK)
