"""Root URL configuration for the user-service."""

from django.contrib import admin
from django.urls import include, path

from core.views.health import health_view
from core.views.swagger import schema_view

urlpatterns = [
    # Documentation
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # Admin
    path("admin/", admin.site.urls),

    # Health check
    path("", health_view, name="health-root"),
    path("health", health_view, name="health"),
    path("health/", health_view, name="health-slash"),

    # Authentication
    path("auth/v1/", include("authentication.urls")),

    # Users
    path("users/v1/", include("users.urls")),
]
