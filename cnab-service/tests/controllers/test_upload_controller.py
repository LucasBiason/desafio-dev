"""Tests for UploadController."""

import uuid
from unittest.mock import MagicMock, patch

from app.controllers.upload_controller import UploadController
from app.models.store import Store
from app.models.transaction_type import TransactionType


def _make_mock_store(created: bool = False) -> tuple[MagicMock, bool]:
    """Creates a mock Store and returns (store, created) tuple."""
    store = MagicMock(spec=Store)
    store.id = uuid.uuid4()
    store.name = "Loja A"
    return store, created


def _make_mock_type(code: int = 1, sign: str = "+") -> MagicMock:
    """Creates a mock TransactionType."""
    tt = MagicMock(spec=TransactionType)
    tt.id = uuid.uuid4()
    tt.code = code
    tt.sign = sign
    return tt


def _make_transaction_dict(**overrides) -> dict:
    """Returns a minimal transaction dict with sensible defaults."""
    base = {
        "type_code": 1,
        "date": "2024-01-15",
        "amount": "150.00",
        "cpf": "12345678901",
        "card": "1234****5678",
        "time": "10:30:00",
        "store_owner": "Joao",
        "store_name": "Loja A",
    }
    base.update(overrides)
    return base


class TestUploadController:
    """Tests for UploadController.process_bulk_transactions."""

    def _make_controller(self) -> UploadController:
        """Creates an UploadController with a mock db session."""
        return UploadController(db=MagicMock())

    def test_processes_transactions_and_returns_summary(self):
        """process_bulk_transactions returns correct total_inserted and stores_created."""
        controller = self._make_controller()
        transactions = [_make_transaction_dict()]

        mock_store, _ = _make_mock_store(created=True)
        mock_type = _make_mock_type()

        with (
            patch.object(controller._store_repo, "get_or_create", return_value=(mock_store, True)),
            patch.object(controller._transaction_repo, "get_type_by_code", return_value=mock_type),
            patch.object(controller._transaction_repo, "exists_by_hash", return_value=False),
            patch.object(controller._transaction_repo, "exists_by_fields", return_value=False),
            patch.object(controller._transaction_repo, "bulk_create", return_value=1),
        ):
            result = controller.process_bulk_transactions(
                upload_id=str(uuid.uuid4()),
                transactions=transactions,
            )

        assert result["total_inserted"] == 1
        assert result["stores_created"] == 1

    def test_existing_store_not_counted_as_created(self):
        """process_bulk_transactions does not increment stores_created for existing stores."""
        controller = self._make_controller()
        transactions = [_make_transaction_dict()]

        mock_store, _ = _make_mock_store(created=False)
        mock_type = _make_mock_type()

        with (
            patch.object(controller._store_repo, "get_or_create", return_value=(mock_store, False)),
            patch.object(controller._transaction_repo, "get_type_by_code", return_value=mock_type),
            patch.object(controller._transaction_repo, "exists_by_hash", return_value=False),
            patch.object(controller._transaction_repo, "exists_by_fields", return_value=False),
            patch.object(controller._transaction_repo, "bulk_create", return_value=1),
        ):
            result = controller.process_bulk_transactions(
                upload_id=str(uuid.uuid4()),
                transactions=transactions,
            )

        assert result["stores_created"] == 0

    def test_unknown_type_code_skips_transaction(self):
        """process_bulk_transactions skips transactions with unrecognised type codes."""
        controller = self._make_controller()
        transactions = [_make_transaction_dict(type_code=99)]

        mock_store, _ = _make_mock_store(created=False)

        with (
            patch.object(controller._store_repo, "get_or_create", return_value=(mock_store, False)),
            patch.object(controller._transaction_repo, "get_type_by_code", return_value=None),
            patch.object(controller._transaction_repo, "bulk_create", return_value=0),
        ):
            result = controller.process_bulk_transactions(
                upload_id=str(uuid.uuid4()),
                transactions=transactions,
            )

        assert result["total_inserted"] == 0

    def test_empty_transactions_returns_zero_summary(self):
        """process_bulk_transactions returns zeros for an empty transaction list."""
        controller = self._make_controller()
        with patch.object(controller._transaction_repo, "bulk_create", return_value=0):
            result = controller.process_bulk_transactions(
                upload_id=str(uuid.uuid4()),
                transactions=[],
            )
        assert result["total_inserted"] == 0
        assert result["stores_created"] == 0

    def test_multiple_transactions_with_new_stores(self):
        """process_bulk_transactions sums stores_created across multiple new stores."""
        controller = self._make_controller()
        transactions = [
            _make_transaction_dict(store_name="Loja A", cpf="11111111111"),
            _make_transaction_dict(store_name="Loja B", cpf="22222222222"),
        ]

        store_a = MagicMock(spec=Store)
        store_a.id = uuid.uuid4()
        store_b = MagicMock(spec=Store)
        store_b.id = uuid.uuid4()

        mock_type = _make_mock_type()

        get_or_create_results = [(store_a, True), (store_b, True)]

        with (
            patch.object(
                controller._store_repo,
                "get_or_create",
                side_effect=get_or_create_results,
            ),
            patch.object(controller._transaction_repo, "get_type_by_code", return_value=mock_type),
            patch.object(controller._transaction_repo, "exists_by_hash", return_value=False),
            patch.object(controller._transaction_repo, "exists_by_fields", return_value=False),
            patch.object(controller._transaction_repo, "bulk_create", return_value=2),
        ):
            result = controller.process_bulk_transactions(
                upload_id=str(uuid.uuid4()),
                transactions=transactions,
            )

        assert result["stores_created"] == 2
        assert result["total_inserted"] == 2

    def test_duplicate_by_hash_skips_transaction(self):
        """process_bulk_transactions skips a transaction when exists_by_hash returns True."""
        controller = self._make_controller()
        transactions = [_make_transaction_dict()]

        mock_store, _ = _make_mock_store(created=False)
        mock_type = _make_mock_type()

        with (
            patch.object(controller._store_repo, "get_or_create", return_value=(mock_store, False)),
            patch.object(controller._transaction_repo, "get_type_by_code", return_value=mock_type),
            patch.object(controller._transaction_repo, "exists_by_hash", return_value=True),
            patch.object(controller._transaction_repo, "bulk_create", return_value=0),
        ):
            result = controller.process_bulk_transactions(
                upload_id=str(uuid.uuid4()),
                transactions=transactions,
            )

        assert result["total_inserted"] == 0

    def test_duplicate_by_fields_skips_transaction(self):
        """process_bulk_transactions skips a transaction when exists_by_fields returns True."""
        controller = self._make_controller()
        transactions = [_make_transaction_dict()]

        mock_store, _ = _make_mock_store(created=False)
        mock_type = _make_mock_type()

        with (
            patch.object(controller._store_repo, "get_or_create", return_value=(mock_store, False)),
            patch.object(controller._transaction_repo, "get_type_by_code", return_value=mock_type),
            patch.object(controller._transaction_repo, "exists_by_hash", return_value=False),
            patch.object(controller._transaction_repo, "exists_by_fields", return_value=True),
            patch.object(controller._transaction_repo, "bulk_create", return_value=0),
        ):
            result = controller.process_bulk_transactions(
                upload_id=str(uuid.uuid4()),
                transactions=transactions,
            )

        assert result["total_inserted"] == 0

    def test_upload_id_preserved_in_result(self):
        """process_bulk_transactions returns the same upload_id that was provided."""
        controller = self._make_controller()
        upload_id = str(uuid.uuid4())
        with patch.object(controller._transaction_repo, "bulk_create", return_value=0):
            result = controller.process_bulk_transactions(
                upload_id=upload_id,
                transactions=[],
            )
        assert result["upload_id"] == upload_id
