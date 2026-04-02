"""Health check response serializer."""

from rest_framework import serializers


class HealthSerializer(serializers.Serializer):
    """Health check response fields."""

    status = serializers.CharField(help_text="Service status (healthy/unhealthy).")
    system_name = serializers.CharField(help_text="Name of the service.")
    version = serializers.CharField(help_text="Current version.")
    environment = serializers.CharField(help_text="Running environment.")
    timestamp = serializers.DateTimeField(help_text="Current timestamp.")
