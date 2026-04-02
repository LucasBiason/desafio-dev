"""URL configuration for the JWT authentication module."""

from django.urls import path

from authentication.views import Login, Validator

urlpatterns = [
    path("login/", Login.as_view(), name="jwt-login"),
    path("validate/", Validator.as_view(), name="jwt-validate"),
]
