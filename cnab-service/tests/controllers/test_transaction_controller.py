"""Tests for TransactionController."""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.controllers.transaction_controller import TransactionController
from app.schemas.transaction_schema import TransactionListResponse, TransactionResponse


def _transaction_row(**overrides) -> dict:
    """Returns a minimal raw SQL result row for a transaction."""
    row = {
        "id": str(uuid.uuid4()),
        "amount": Decimal("100.00"),
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
    row.update(overrides)
    return row


class TestTransactionController:
    """Tests for TransactionController methods."""

    def _make_controller(self) -> TransactionController:
        """Creates a TransactionController with a mock db session."""
        return TransactionController(db=MagicMock())

    def test_build_response_creates_correct_transaction_response(self):
        """_build_response maps all raw row fields to a TransactionResponse."""
        row = _transaction_row()

        result = TransactionController._build_response(row)

        assert isinstance(result, TransactionResponse)
        assert result.id == row["id"]
        assert result.amount == row["amount"]
        assert result.card == row["card"]
        assert result.occurred_at == row["occurred_at"]
        assert result.occurred_time == row["occurred_time"]
        assert result.transaction_type.id == row["transaction_type_id"]
        assert result.transaction_type.code == row["transaction_type_code"]
        assert result.transaction_type.description == row["transaction_type_description"]
        assert result.transaction_type.nature == row["transaction_type_nature"]
        assert result.transaction_type.sign == row["transaction_type_sign"]
        assert result.store["id"] == row["store_id"]
        assert result.store["name"] == row["store_name"]
        assert result.store["owner_name"] == row["store_owner_name"]
        assert result.store["owner_cpf"] == row["store_owner_cpf"]

    def test_list_by_store_returns_transaction_list_response_with_count_and_results(self):
        """list_by_store converts repo rows to TransactionListResponse."""
        controller = self._make_controller()
        store_id = str(uuid.uuid4())
        row = _transaction_row()
        with patch.object(
            controller._transaction_repo,
            "list_by_store",
            return_value=([row], 1),
        ):
            result = controller.list_by_store(store_id=store_id)

        assert isinstance(result, TransactionListResponse)
        assert result.count == 1
        assert len(result.results) == 1
        assert isinstance(result.results[0], TransactionResponse)

    def test_list_by_store_passes_filters_to_repo(self):
        """list_by_store forwards all filter parameters to the repository."""
        controller = self._make_controller()
        store_id = str(uuid.uuid4())
        with patch.object(
            controller._transaction_repo,
            "list_by_store",
            return_value=([], 0),
        ) as mock_list:
            controller.list_by_store(
                store_id=store_id,
                page=2,
                page_size=5,
                type_codes=[1],
                nature="Entrada",
                date_from="2024-01-01",
                date_to="2024-12-31",
            )

        mock_list.assert_called_once_with(
            store_id=store_id,
            page=2,
            page_size=5,
            type_codes=[1],
            nature="Entrada",
            date_from="2024-01-01",
            date_to="2024-12-31",
        )

    def test_list_by_store_empty_returns_count_zero_and_empty_results(self):
        """list_by_store returns TransactionListResponse(count=0, results=[]) when repo is empty."""
        controller = self._make_controller()
        with patch.object(
            controller._transaction_repo,
            "list_by_store",
            return_value=([], 0),
        ):
            result = controller.list_by_store(store_id=str(uuid.uuid4()))

        assert isinstance(result, TransactionListResponse)
        assert result.count == 0
        assert result.results == []

    def test_get_transaction_returns_transaction_response_when_found(self):
        """get_transaction returns a TransactionResponse when the repo finds the row."""
        controller = self._make_controller()
        transaction_id = str(uuid.uuid4())
        row = _transaction_row()
        with patch.object(
            controller._transaction_repo,
            "query_one",
            return_value=row,
        ):
            result = controller.get_transaction(transaction_id=transaction_id)

        assert isinstance(result, TransactionResponse)
        assert result.id == row["id"]

    def test_get_transaction_returns_none_when_not_found(self):
        """get_transaction returns None when query_one returns None."""
        controller = self._make_controller()
        with patch.object(
            controller._transaction_repo,
            "query_one",
            return_value=None,
        ):
            result = controller.get_transaction(transaction_id=str(uuid.uuid4()))

        assert result is None
