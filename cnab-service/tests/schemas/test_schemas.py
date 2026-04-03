"""Tests for all cnab-service Pydantic schemas."""

from decimal import Decimal

from app.schemas.internal_schema import BulkTransactionRequest, BulkTransactionResponse, TransactionInput
from app.schemas.store_schema import StoreListResponse, StoreResponse
from app.schemas.transaction_schema import TransactionListResponse, TransactionResponse, TransactionTypeResponse


class TestStoreResponse:
    """Tests for StoreResponse schema."""

    def test_defaults_are_zero(self):
        """StoreResponse defaults balance and totals to zero."""
        store = StoreResponse(
            id="some-uuid",
            name="Loja A",
            owner_name="Joao",
            owner_cpf="12345678901",
        )
        assert store.balance == Decimal("0.00")
        assert store.total_income == Decimal("0.00")
        assert store.total_expense == Decimal("0.00")
        assert store.transaction_count == 0

    def test_with_balance_fields(self):
        """StoreResponse accepts decimal balance fields."""
        store = StoreResponse(
            id="some-uuid",
            name="Loja B",
            owner_name="Maria",
            owner_cpf="98765432100",
            balance=Decimal("1500.00"),
            total_income=Decimal("2000.00"),
            total_expense=Decimal("500.00"),
            transaction_count=10,
        )
        assert store.balance == Decimal("1500.00")
        assert store.transaction_count == 10


class TestStoreListResponse:
    """Tests for StoreListResponse schema."""

    def test_count_and_results(self):
        """StoreListResponse wraps count and results correctly."""
        store = StoreResponse(id="x", name="A", owner_name="B", owner_cpf="12345678901")
        response = StoreListResponse(count=1, results=[store])
        assert response.count == 1
        assert len(response.results) == 1

    def test_empty_results(self):
        """StoreListResponse accepts empty results list."""
        response = StoreListResponse(count=0, results=[])
        assert response.count == 0
        assert response.results == []


class TestTransactionTypeResponse:
    """Tests for TransactionTypeResponse schema."""

    def test_all_fields(self):
        """TransactionTypeResponse validates all required fields."""
        tt = TransactionTypeResponse(
            id="uuid-tt",
            code=1,
            description="Debito",
            nature="Entrada",
            sign="+",
        )
        assert tt.code == 1
        assert tt.sign == "+"

    def test_from_attributes(self):
        """TransactionTypeResponse supports from_attributes ORM mode."""
        from unittest.mock import MagicMock

        mock_type = MagicMock()
        mock_type.id = "abc"
        mock_type.code = 3
        mock_type.description = "Financiamento"
        mock_type.nature = "Saida"
        mock_type.sign = "-"
        result = TransactionTypeResponse.model_validate(mock_type)
        assert result.code == 3


class TestTransactionResponse:
    """Tests for TransactionResponse schema."""

    def _make_type(self):
        return TransactionTypeResponse(id="t", code=1, description="D", nature="E", sign="+")

    def test_minimal_fields(self):
        """TransactionResponse accepts minimal required fields."""
        tx = TransactionResponse(
            id="tx-uuid",
            transaction_type=self._make_type(),
            amount=Decimal("100.00"),
            card="1234****5678",
            occurred_at="2024-01-15",
            occurred_time="10:30:00",
        )
        assert tx.store is None
        assert tx.amount == Decimal("100.00")

    def test_with_store_dict(self):
        """TransactionResponse accepts a store dict."""
        tx = TransactionResponse(
            id="tx-uuid",
            transaction_type=self._make_type(),
            amount=Decimal("50.00"),
            card="0000****1111",
            occurred_at="2024-03-01",
            occurred_time="08:00:00",
            store={"id": "s-uuid", "name": "Loja C"},
        )
        assert tx.store["name"] == "Loja C"


class TestTransactionListResponse:
    """Tests for TransactionListResponse schema."""

    def test_pagination_fields(self):
        """TransactionListResponse has count and results."""
        response = TransactionListResponse(count=0, results=[])
        assert response.count == 0


class TestTransactionInput:
    """Tests for TransactionInput schema."""

    def test_valid_input(self):
        """TransactionInput accepts all required fields."""
        item = TransactionInput(
            type_code=1,
            date="2024-01-15",
            amount="150.00",
            cpf="12345678901",
            card="1234****5678",
            time="10:30:00",
            store_owner="Joao",
            store_name="Loja D",
        )
        assert item.type_code == 1
        assert item.amount == "150.00"


class TestBulkTransactionRequest:
    """Tests for BulkTransactionRequest schema."""

    def test_empty_transactions(self):
        """BulkTransactionRequest accepts empty transaction list."""
        request = BulkTransactionRequest(upload_id="upload-uuid", transactions=[])
        assert request.upload_id == "upload-uuid"
        assert request.transactions == []

    def test_with_transactions(self):
        """BulkTransactionRequest accepts a list of TransactionInput objects."""
        item = TransactionInput(
            type_code=2,
            date="2024-02-01",
            amount="200.00",
            cpf="98765432100",
            card="5555****4444",
            time="14:00:00",
            store_owner="Maria",
            store_name="Loja E",
        )
        request = BulkTransactionRequest(upload_id="up-001", transactions=[item])
        assert len(request.transactions) == 1


class TestBulkTransactionResponse:
    """Tests for BulkTransactionResponse schema."""

    def test_summary_fields(self):
        """BulkTransactionResponse serializes summary correctly."""
        response = BulkTransactionResponse(
            upload_id="up-001",
            total_inserted=5,
            stores_created=2,
        )
        assert response.total_inserted == 5
        assert response.stores_created == 2
