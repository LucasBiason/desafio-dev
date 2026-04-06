"""ViewSet for user management endpoints."""

import logging

from rest_framework import mixins, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from authentication.controllers.auth_controller import JWTAuthentication
from users.controllers.user import UserController
from users.models.user import User
from users.serializers.user import UserSerializer

logger = logging.getLogger(__name__)


class ManageUserView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """User management ViewSet. JWT auth is validated manually per request."""

    permission_classes = []
    authentication_classes = []

    def set_controller(self, request: Request) -> UserController:
        """Validate the JWT token and return a UserController for the authenticated user."""
        logged_user: User = JWTAuthentication.validate(request, return_user=True)
        return UserController(logged_user)

    def get_serializer(self, *args, **kwargs) -> UserSerializer:
        return UserSerializer(*args, **kwargs)

    def get_queryset(self):
        controller = self.set_controller(self.request)
        return controller.list_users()

    def list(self, request: Request, *args, **kwargs) -> Response:
        controller = self.set_controller(request)
        filters = {k: v for k, v in request.query_params.items()}
        users = controller.list_users(filters=filters)
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, pk: str | None = None, *args, **kwargs) -> Response:
        controller = self.set_controller(request)
        user = controller.retrieve(int(pk))
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request: Request, *args, **kwargs) -> Response:
        controller = self.set_controller(request)
        user = controller.create_user(dict(request.data))
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, pk: str | None = None, *args, **kwargs) -> Response:
        controller = self.set_controller(request)
        user = controller.update_user(int(pk), dict(request.data))
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request: Request, pk: str | None = None, *args, **kwargs) -> Response:
        controller = self.set_controller(request)
        controller.destroy_user(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
