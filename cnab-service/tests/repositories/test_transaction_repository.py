"""Tests for TransactionRepository."""

import uuid
from unittest.mock import patch

from app.models.transaction_type import TransactionType
from app.repositories.transaction_repository import TransactionRepository


def _make_transaction_type(db, code: int = 1, sign: str = "+") -> TransactionType:
    """Persists a TransactionType and returns it."""
    tt = TransactionType()
    tt.code = code
    tt.description = f"Type {code}"
    tt.nature = "Entrada" if sign == "+" else "Saida"
    tt.sign = sign
    db.add(tt)
    db.commit()
    db.refresh(tt)
    return tt


class TestTransactionRepositoryGetAllTypes:
    """Tests for TransactionRepository.get_all_types."""

    def test_returns_all_types_ordered_by_code(self, db):
        """get_all_types returns all types ordered ascending by code."""
        _make_transaction_type(db, code=3, sign="-")
        _make_transaction_type(db, code=1, sign="+")
        _make_transaction_type(db, code=2, sign="+")
        repo = TransactionRepository(db=db)
        types = repo.get_all_types()
        codes = [t.code for t in types]
        assert codes == sorted(codes)

    def test_returns_empty_list_when_no_types(self, db):
        """get_all_types returns an empty list when the table is empty."""
        repo = TransactionRepository(db=db)
        types = repo.get_all_types()
        assert types == []


class TestTransactionRepositoryGetTypeByCode:
    """Tests for TransactionRepository.get_type_by_code."""

    def test_returns_matching_type(self, db):
        """get_type_by_code returns the correct TransactionType for a valid code."""
        _make_transaction_type(db, code=5)
        repo = TransactionRepository(db=db)
        result = repo.get_type_by_code(5)
        assert result is not None
        assert result.code == 5

    def test_returns_none_for_unknown_code(self, db):
        """get_type_by_code returns None when the code does not exist."""
        repo = TransactionRepository(db=db)
        result = repo.get_type_by_code(99)
        assert result is None


class TestTransactionRepositoryListByStore:
    """Tests for TransactionRepository.list_by_store using mocked SQL helpers."""

    def test_returns_rows_and_total(self, db):
        """list_by_store returns (rows, total) from the underlying SQL query."""
        repo = TransactionRepository(db=db)
        mock_rows = [
            {
                "id": str(uuid.uuid4()),
                "amount": "100.00",
                "card": "1234****5678",
                "occurred_at": "2024-01-15",
                "occurred_time": "10:30:00",
                "transaction_type_id": str(uuid.uuid4()),
                "transaction_type_code": 1,
                "transaction_type_description": "Debito",
                "transaction_type_nature": "Entrada",
                "transaction_type_sign": "+",
                "store_id": str(uuid.uuid4()),
                "store_name": "Loja A",
                "store_owner_name": "Joao",
                "store_owner_cpf": "12345678901",
            }
        ]
        with (
            patch.object(repo, "query_one", return_value={"total": 1}),
            patch.object(repo, "query_list", return_value=mock_rows),
        ):
            rows, total = repo.list_by_store(store_id=str(uuid.uuid4()))

        assert total == 1
        assert len(rows) == 1
        assert rows[0]["card"] == "1234****5678"

    def test_type_code_filter_in_params(self, db):
        """list_by_store passes type_code to SQL params when provided."""
        repo = TransactionRepository(db=db)
        with (
            patch.object(repo, "query_one", return_value={"total": 0}),
            patch.object(repo, "query_list", return_value=[]) as mock_list,
        ):
            repo.list_by_store(store_id=str(uuid.uuid4()), type_code=3)
            call_params = mock_list.call_args[0][1]
            assert call_params.get("type_code") == 3

    def test_nature_filter_in_params(self, db):
        """list_by_store passes nature to SQL params when provided."""
        repo = TransactionRepository(db=db)
        with (
            patch.object(repo, "query_one", return_value={"total": 0}),
            patch.object(repo, "query_list", return_value=[]) as mock_list,
        ):
            repo.list_by_store(store_id=str(uuid.uuid4()), nature="Entrada")
            call_params = mock_list.call_args[0][1]
            assert call_params.get("nature") == "Entrada"

    def test_date_filters_in_params(self, db):
        """list_by_store includes date_from and date_to in SQL params."""
        repo = TransactionRepository(db=db)
        with (
            patch.object(repo, "query_one", return_value={"total": 0}),
            patch.object(repo, "query_list", return_value=[]) as mock_list,
        ):
            repo.list_by_store(
                store_id=str(uuid.uuid4()),
                date_from="2024-01-01",
                date_to="2024-12-31",
            )
            call_params = mock_list.call_args[0][1]
            assert call_params.get("date_from") == "2024-01-01"
            assert call_params.get("date_to") == "2024-12-31"

    def test_pagination_offset_is_correct(self, db):
        """list_by_store calculates offset as (page-1)*page_size."""
        repo = TransactionRepository(db=db)
        with (
            patch.object(repo, "query_one", return_value={"total": 50}),
            patch.object(repo, "query_list", return_value=[]) as mock_list,
        ):
            repo.list_by_store(store_id=str(uuid.uuid4()), page=2, page_size=15)
            call_params = mock_list.call_args[0][1]
            assert call_params["offset"] == 15
            assert call_params["limit"] == 15

    def test_empty_result_returns_zero_total(self, db):
        """list_by_store returns ([], 0) when no transactions match."""
        repo = TransactionRepository(db=db)
        with (
            patch.object(repo, "query_one", return_value={"total": 0}),
            patch.object(repo, "query_list", return_value=[]),
        ):
            rows, total = repo.list_by_store(store_id=str(uuid.uuid4()))
        assert rows == []
        assert total == 0


class TestTransactionRepositoryBulkCreate:
    """Tests for TransactionRepository.bulk_create."""

    def test_bulk_create_returns_count(self, db):
        """bulk_create returns the number of transactions added to the session."""
        from unittest.mock import patch

        repo = TransactionRepository(db=db)
        with patch.object(repo.db, "add"), patch.object(repo.db, "flush"):
            count = repo.bulk_create(["tx1", "tx2", "tx3"])
        assert count == 3

    def test_bulk_create_empty_list(self, db):
        """bulk_create returns 0 for an empty list."""
        repo = TransactionRepository(db=db)
        count = repo.bulk_create([])
        assert count == 0
