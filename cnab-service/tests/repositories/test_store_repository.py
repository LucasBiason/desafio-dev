"""Tests for StoreRepository."""

import uuid
from unittest.mock import patch

from app.models.store import Store
from app.repositories.store_repository import StoreRepository


def _make_store(db, name="Loja A", owner_name="Joao", owner_cpf="12345678901") -> Store:
    """Persists a Store record and returns it."""
    store = Store()
    store.name = name
    store.owner_name = owner_name
    store.owner_cpf = owner_cpf
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


class TestStoreRepositoryGetOrCreate:
    """Tests for StoreRepository.get_or_create."""

    def test_creates_new_store(self, db):
        """get_or_create returns created=True when the store does not exist."""
        repo = StoreRepository(db=db)
        store, created = repo.get_or_create(
            name="Loja Nova",
            owner_name="Pedro",
            owner_cpf="11111111111",
        )
        assert created is True
        assert store.name == "Loja Nova"
        assert store.owner_cpf == "11111111111"

    def test_returns_existing_store(self, db):
        """get_or_create returns created=False when the store already exists."""
        _make_store(db, name="Loja Existente", owner_cpf="22222222222")
        repo = StoreRepository(db=db)
        store, created = repo.get_or_create(
            name="Loja Existente",
            owner_name="Qualquer",
            owner_cpf="22222222222",
        )
        assert created is False
        assert store.name == "Loja Existente"

    def test_different_cpf_creates_new_store(self, db):
        """get_or_create treats stores with same name but different CPF as distinct."""
        _make_store(db, name="Loja X", owner_cpf="33333333333")
        repo = StoreRepository(db=db)
        _, created = repo.get_or_create(
            name="Loja X",
            owner_name="Outro",
            owner_cpf="44444444444",
        )
        assert created is True


class TestStoreRepositoryGetById:
    """Tests for StoreRepository.get_by_id."""

    def test_returns_store_by_id(self, db):
        """get_by_id returns the correct store record."""
        store = _make_store(db)
        repo = StoreRepository(db=db)
        found = repo.get_by_id(store.id)
        assert found is not None
        assert found.id == store.id

    def test_returns_none_for_missing_id(self, db):
        """get_by_id returns None when the UUID does not exist."""
        repo = StoreRepository(db=db)
        found = repo.get_by_id(uuid.uuid4())
        assert found is None


class TestStoreRepositoryListWithBalance:
    """Tests for StoreRepository.list_with_balance using mocked query_list."""

    def test_returns_rows_and_total(self, db):
        """list_with_balance returns (rows, total) tuple from the underlying SQL."""
        repo = StoreRepository(db=db)
        mock_rows = [
            {
                "id": str(uuid.uuid4()),
                "name": "Loja A",
                "owner_name": "Joao",
                "owner_cpf": "12345678901",
                "balance": "100.00",
                "total_income": "200.00",
                "total_expense": "100.00",
                "transaction_count": 3,
            }
        ]
        with (
            patch.object(repo, "query_one", return_value={"total": 1}),
            patch.object(repo, "query_list", return_value=mock_rows),
        ):
            rows, total = repo.list_with_balance(page=1, page_size=10)

        assert total == 1
        assert len(rows) == 1
        assert rows[0]["name"] == "Loja A"

    def test_name_filter_passes_ilike_pattern(self, db):
        """list_with_balance passes a LIKE-wrapped name filter to the SQL."""
        repo = StoreRepository(db=db)
        with (
            patch.object(repo, "query_one", return_value={"total": 0}),
            patch.object(repo, "query_list", return_value=[]) as mock_list,
        ):
            repo.list_with_balance(name_filter="Loja")
            call_params = mock_list.call_args[0][1]
            assert "name_filter" in call_params
            assert "Loja" in call_params["name_filter"]

    def test_owner_filter_passes_ilike_pattern(self, db):
        """list_with_balance passes a LIKE-wrapped owner filter to the SQL."""
        repo = StoreRepository(db=db)
        with (
            patch.object(repo, "query_one", return_value={"total": 0}),
            patch.object(repo, "query_list", return_value=[]) as mock_list,
        ):
            repo.list_with_balance(owner_filter="Pedro")
            call_params = mock_list.call_args[0][1]
            assert "owner_filter" in call_params

    def test_empty_result_returns_zero_total(self, db):
        """list_with_balance returns ([], 0) when no stores match."""
        repo = StoreRepository(db=db)
        with (
            patch.object(repo, "query_one", return_value={"total": 0}),
            patch.object(repo, "query_list", return_value=[]),
        ):
            rows, total = repo.list_with_balance()
        assert total == 0
        assert rows == []

    def test_pagination_offset_calculated(self, db):
        """list_with_balance correctly calculates offset for page > 1."""
        repo = StoreRepository(db=db)
        with (
            patch.object(repo, "query_one", return_value={"total": 30}),
            patch.object(repo, "query_list", return_value=[]) as mock_list,
        ):
            repo.list_with_balance(page=3, page_size=10)
            call_params = mock_list.call_args[0][1]
            assert call_params["offset"] == 20
            assert call_params["limit"] == 10
