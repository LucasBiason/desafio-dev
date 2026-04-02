"""Swagger/OpenAPI documentation configuration."""

import os

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="CNAB Parser - User Service",
        default_version=os.getenv("SYSTEM_VERSION", "0.1.0"),
        description="User authentication and management service.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
