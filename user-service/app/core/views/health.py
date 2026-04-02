"""Health check endpoint for the user-service."""

import os

from django.utils.timezone import now
from drf_yasg.utils import swagger_auto_schema
from rest_framework import views
from rest_framework.request import Request
from rest_framework.response import Response

from core.serializers.health import HealthSerializer

SERVICE_NAME = "user-service"
DEFAULT_VERSION = "0.1.0"


class HealthView(views.APIView):
    """GET /health — returns service name, version and current timestamp."""

    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        responses={200: HealthSerializer(), 500: "Server error.", 404: "Not found."},
        operation_id="Health Check",
        operation_description="Check whether the service is running and responsive.",
    )
    def get(self, request: Request, format: str = None) -> Response:
        return Response({
            "service": SERVICE_NAME,
            "version": os.getenv("SYSTEM_VERSION", DEFAULT_VERSION) or DEFAULT_VERSION,
            "dt": now(),
        })


health_view = HealthView.as_view()
