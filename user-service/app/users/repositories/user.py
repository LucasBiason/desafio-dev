"""Repository for user data access."""

from django.db.models import Q

from users.models.user import User


class UserRepository:
    """Database access layer for the User model."""

    def retrieve(self, user_pk: int) -> User | None:
        """Return the user with the given PK, or None if not found."""
        return User.objects.filter(pk=user_pk).first()

    def retrieve_by_username(self, username: str, exclude_user_id: int | None = None) -> User | None:
        """Return the user with the given username, optionally excluding one user by PK."""
        qs = User.objects.filter(username=username)
        if exclude_user_id is not None:
            qs = qs.exclude(pk=exclude_user_id)
        return qs.first()

    def retrieve_by_email(self, email: str, exclude_user_id: int | None = None) -> User | None:
        """Return the user with the given email, optionally excluding one user by PK."""
        qs = User.objects.filter(email=email)
        if exclude_user_id is not None:
            qs = qs.exclude(pk=exclude_user_id)
        return qs.first()

    def queryset(self, **kwargs) -> list[User]:
        """Return a filtered queryset based on dynamic keyword arguments.

        Supported filters: id, is_active, username (icontains), email (icontains),
        name (icontains on first_name or last_name), order_by (default: "id").
        """
        filters = Q()
        order_by = kwargs.pop("order_by", "id")

        if "id" in kwargs:
            filters &= Q(id=kwargs["id"])
        if "is_active" in kwargs:
            value = kwargs["is_active"]
            if isinstance(value, str):
                value = value.lower() in ("true", "1", "t")
            filters &= Q(is_active=value)
        if "username" in kwargs:
            filters &= Q(username__icontains=kwargs["username"])
        if "email" in kwargs:
            filters &= Q(email__icontains=kwargs["email"])
        if "name" in kwargs:
            name = kwargs["name"]
            filters &= Q(first_name__icontains=name) | Q(last_name__icontains=name)

        return User.objects.filter(filters).order_by(order_by)

    def save(self, data: dict, user: User | None = None) -> User:
        """Create a new user or update an existing one from the given data dict.

        Fields are assigned explicitly to avoid unintended mass assignment.
        """
        if user is None:
            user = User.objects.create_user(
                username=data.get("username", ""),
                email=data.get("email", ""),
                password=data.get("password", ""),
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
            )
            return user

        if "username" in data:
            user.username = data["username"]
        if "email" in data:
            user.email = data["email"]
        if "first_name" in data:
            user.first_name = data["first_name"]
        if "last_name" in data:
            user.last_name = data["last_name"]
        if "is_active" in data:
            user.is_active = data["is_active"]
        if "password" in data:
            user.set_password(data["password"])

        user.save()
        return user

    def destroy(self, user: User) -> User:
        """Set the user as inactive and save."""
        user.is_active = False
        user.save()
        return user
