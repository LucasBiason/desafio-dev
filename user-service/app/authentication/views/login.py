"""API endpoint for user login."""

import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication import schemas
from authentication.controllers.auth_controller import JWTAuthentication

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class Login(APIView):
    """POST /login — authenticate and return a JWT token."""

    permission_classes = []
    authentication_classes = []

    @schemas.login
    def post(self, request) -> Response:
        logged_user: dict = JWTAuthentication.login(request)
        return Response(logged_user, status=status.HTTP_200_OK)
