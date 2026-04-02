"""Health check response serializer."""

from rest_framework import serializers


class HealthSerializer(serializers.Serializer):
    """Health check response fields."""

    service = serializers.CharField(help_text="Name of the service.")
    version = serializers.CharField(help_text="Current version of the service.")
    dt = serializers.DateTimeField(help_text="Timestamp of the health check request.")
