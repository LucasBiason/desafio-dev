"""Swagger schema definitions for the authentication endpoints."""

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from authentication.serializers.login_serializer import LoginSerializer

BAD_REQUEST = "Bad request."
NOT_AUTHORIZED = "Not authorized."
NOT_FOUND = "Not found."


class ResponseSchema:
    """Builds standard response dicts for Swagger decorators."""

    @classmethod
    def responses(cls, schema_serializer=None) -> dict:
        """Return the standard 200/400/403/404 response map for a given serializer."""
        return {
            200: schema_serializer if schema_serializer else {},
            400: BAD_REQUEST,
            403: NOT_AUTHORIZED,
            404: NOT_FOUND,
        }


login = swagger_auto_schema(
    responses=ResponseSchema.responses(LoginSerializer()),
    operation_id="Login",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["username", "password"],
        properties={
            "username": openapi.Schema(
                type=openapi.TYPE_STRING, description="The username of the user."
            ),
            "password": openapi.Schema(
                type=openapi.TYPE_STRING, description="The password of the user."
            ),
        },
    ),
    operation_description=(
        "Generates authentication information for the logged-in user and returns a token "
        "to be used in other services, as well as the data of the user."
    ),
)

validate = swagger_auto_schema(
    responses=ResponseSchema.responses(LoginSerializer()),
    operation_id="Validate Token",
    operation_description=(
        "Validates the authentication data to verify that the user is logged in and active. "
        "Returns the same data. Use this method to validate the token received in your requests."
    ),
)
