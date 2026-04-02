"""UserSerializer tests."""

import pytest

from users.models.user import User
from users.serializers.user import UserSerializer


@pytest.mark.django_db
class TestUserSerializerFields:
    """UserSerializer field output."""

    def test_serializer_outputs_correct_fields(self) -> None:
        """Serialized output contains all expected fields."""
        user = User.objects.create_user(
            username="serializeruser",
            email="serializer@example.com",
            password="pass12345",
            first_name="Serializer",
            last_name="Test",
        )
        serializer = UserSerializer(user)
        data = serializer.data

        expected_fields = {"id", "username", "email", "first_name", "last_name", "is_active", "is_staff", "created_at", "updated_at"}
        assert expected_fields.issubset(set(data.keys()))

    def test_serializer_read_only_fields(self) -> None:
        """id, created_at and updated_at are read-only."""
        read_only_fields = {
            field.field_name
            for field in UserSerializer().fields.values()
            if field.read_only
        }

        assert "id" in read_only_fields
        assert "created_at" in read_only_fields
        assert "updated_at" in read_only_fields

    def test_password_field_is_write_only(self) -> None:
        """Password is absent from serialized output."""
        user = User.objects.create_user(
            username="passwordcheck",
            email="passwordcheck@example.com",
            password="secret12345",
        )
        serializer = UserSerializer(user)
        data = serializer.data

        assert "password" not in data

    def test_password_field_is_write_only_flag(self) -> None:
        """Password field has write_only=True."""
        password_field = UserSerializer().fields["password"]

        assert password_field.write_only is True
