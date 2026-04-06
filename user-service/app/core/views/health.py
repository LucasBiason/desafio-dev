"""Health check endpoints for the user-service."""

import os

from django.db import connection
from django.utils.timezone import now
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, views
from rest_framework.request import Request
from rest_framework.response import Response

from core.serializers.health import HealthSerializer

SERVICE_NAME = "user-service"
DEFAULT_VERSION = "0.1.0"


class HealthView(views.APIView):
    """GET /health — service status, version and timestamp."""

    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        responses={200: HealthSerializer(), 500: "Server error."},
        operation_id="Health Check",
        operation_description="Check whether the service is running.",
    )
    def get(self, request: Request, format: str = None) -> Response:
        return Response(
            {
                "status": "healthy",
                "system_name": SERVICE_NAME,
                "version": os.getenv("SYSTEM_VERSION", DEFAULT_VERSION) or DEFAULT_VERSION,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "timestamp": now(),
            }
        )


class ReadinessView(views.APIView):
    """GET /health/ready — checks database connection."""

    authentication_classes = []
    permission_classes = []

    def get(self, request: Request, format: str = None) -> Response:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return Response(
                {
                    "status": "ready",
                    "system_name": SERVICE_NAME,
                    "timestamp": now(),
                }
            )
        except Exception as e:
            return Response(
                {
                    "status": "not_ready",
                    "system_name": SERVICE_NAME,
                    "error": str(e),
                    "timestamp": now(),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class LivenessView(views.APIView):
    """GET /health/live — simple alive check."""

    authentication_classes = []
    permission_classes = []

    def get(self, request: Request, format: str = None) -> Response:
        return Response(
            {
                "status": "alive",
                "system_name": SERVICE_NAME,
                "timestamp": now(),
            }
        )


health_view = HealthView.as_view()
readiness_view = ReadinessView.as_view()
liveness_view = LivenessView.as_view()
