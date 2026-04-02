"""UserRepository tests."""

import pytest

from users.models.user import User
from users.repositories.user import UserRepository


@pytest.fixture
def repo() -> UserRepository:
    """UserRepository instance."""
    return UserRepository()


@pytest.fixture
def sample_user(db) -> User:
    """Persisted test user for repository tests."""
    return User.objects.create_user(
        username="repouser",
        email="repouser@example.com",
        password="pass123",
        first_name="Repo",
        last_name="User",
    )


@pytest.mark.django_db
class TestRetrieveByUsername:
    """UserRepository.retrieve_by_username."""

    def test_retrieve_by_username_found(self, repo: UserRepository, sample_user: User) -> None:
        """Existing username returns the user."""
        result = repo.retrieve_by_username("repouser")

        assert result is not None
        assert result.username == "repouser"

    def test_retrieve_by_username_not_found(self, repo: UserRepository) -> None:
        """Unknown username returns None."""
        result = repo.retrieve_by_username("nonexistent")

        assert result is None

    def test_retrieve_by_username_with_exclude(self, repo: UserRepository, sample_user: User) -> None:
        """Excluded user id returns None even when username matches."""
        result = repo.retrieve_by_username("repouser", exclude_user_id=sample_user.pk)

        assert result is None


@pytest.mark.django_db
class TestRetrieveByEmail:
    """UserRepository.retrieve_by_email."""

    def test_retrieve_by_email_found(self, repo: UserRepository, sample_user: User) -> None:
        """Existing email returns the user."""
        result = repo.retrieve_by_email("repouser@example.com")

        assert result is not None
        assert result.email == "repouser@example.com"

    def test_retrieve_by_email_not_found(self, repo: UserRepository) -> None:
        """Unknown email returns None."""
        result = repo.retrieve_by_email("nobody@example.com")

        assert result is None

    def test_retrieve_by_email_with_exclude(self, repo: UserRepository, sample_user: User) -> None:
        """Excluded user id returns None even when email matches."""
        result = repo.retrieve_by_email("repouser@example.com", exclude_user_id=sample_user.pk)

        assert result is None


@pytest.mark.django_db
class TestQueryset:
    """UserRepository.queryset with various filters."""

    def test_filter_by_username(self, repo: UserRepository, sample_user: User) -> None:
        """Filters by partial case-insensitive username."""
        results = list(repo.queryset(username="REPOUSER"))

        assert any(u.username == "repouser" for u in results)

    def test_filter_by_email(self, repo: UserRepository, sample_user: User) -> None:
        """Filters by partial case-insensitive email."""
        results = list(repo.queryset(email="repouser@"))

        assert any(u.email == "repouser@example.com" for u in results)

    def test_filter_by_name(self, repo: UserRepository, sample_user: User) -> None:
        """Filters by partial first name match."""
        results = list(repo.queryset(name="repo"))

        assert any(u.username == "repouser" for u in results)

    def test_filter_by_name_matches_last_name(self, repo: UserRepository, sample_user: User) -> None:
        """Filters by partial last name match."""
        results = list(repo.queryset(name="user"))

        assert any(u.username == "repouser" for u in results)

    def test_custom_order_by(self, repo: UserRepository) -> None:
        """Results are ordered by the given field."""
        User.objects.create_user(username="aaa_order", email="aaa@example.com", password="pass123")
        User.objects.create_user(username="zzz_order", email="zzz@example.com", password="pass123")

        results = list(repo.queryset(order_by="username"))

        usernames = [u.username for u in results]
        assert usernames == sorted(usernames)

    def test_filter_by_id(self, repo: UserRepository, sample_user: User) -> None:
        """Filters by exact primary key."""
        results = list(repo.queryset(id=sample_user.pk))

        assert len(results) == 1
        assert results[0].pk == sample_user.pk

    def test_filter_by_is_active_bool(self, repo: UserRepository, sample_user: User) -> None:
        """Filters by is_active boolean."""
        results = list(repo.queryset(is_active=True))

        assert any(u.pk == sample_user.pk for u in results)

    def test_filter_by_is_active_string_true(self, repo: UserRepository, sample_user: User) -> None:
        """String 'true' is coerced to True when filtering by is_active."""
        results = list(repo.queryset(is_active="true"))

        assert any(u.pk == sample_user.pk for u in results)

    def test_filter_by_is_active_string_false(self, repo: UserRepository, sample_user: User) -> None:
        """String 'false' is coerced to False when filtering by is_active."""
        results = list(repo.queryset(is_active="false"))

        assert not any(u.pk == sample_user.pk for u in results)

    def test_no_filters_returns_all(self, repo: UserRepository, sample_user: User) -> None:
        """No filters returns all users."""
        results = list(repo.queryset())

        assert len(results) >= 1


@pytest.mark.django_db
class TestSave:
    """UserRepository.save."""

    def test_save_existing_user_with_new_password(self, repo: UserRepository, sample_user: User) -> None:
        """Password in update data is hashed and persisted."""
        result = repo.save({"first_name": "Updated", "password": "newpassword99"}, user=sample_user)

        assert result.check_password("newpassword99")

    def test_save_existing_user_updates_last_name(self, repo: UserRepository, sample_user: User) -> None:
        """last_name is updated and persisted."""
        result = repo.save({"last_name": "NewLast"}, user=sample_user)

        assert result.last_name == "NewLast"
        sample_user.refresh_from_db()
        assert sample_user.last_name == "NewLast"

    def test_save_existing_user_updates_is_active(self, repo: UserRepository, sample_user: User) -> None:
        """is_active is updated and persisted."""
        result = repo.save({"is_active": False}, user=sample_user)

        assert result.is_active is False
        sample_user.refresh_from_db()
        assert sample_user.is_active is False


@pytest.mark.django_db
class TestDestroy:
    """UserRepository.destroy."""

    def test_destroy_marks_user_inactive(self, repo: UserRepository, sample_user: User) -> None:
        """Sets is_active to False and persists."""
        assert sample_user.is_active is True

        result = repo.destroy(sample_user)

        assert result.is_active is False
        sample_user.refresh_from_db()
        assert sample_user.is_active is False
