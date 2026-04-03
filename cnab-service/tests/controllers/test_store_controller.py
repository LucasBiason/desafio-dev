"""Tests for StoreController."""

import uuid
from unittest.mock import MagicMock, patch

from app.controllers.store_controller import StoreController


class TestStoreController:
    """Tests for StoreController methods."""

    def _make_controller(self) -> StoreController:
        """Creates a StoreController with a mock db session."""
        return StoreController(db=MagicMock())

    def test_list_stores_delegates_to_repository(self):
        """list_stores returns results from the store repository."""
        controller = self._make_controller()
        mock_rows = [{"id": str(uuid.uuid4()), "name": "Loja A"}]
        with patch.object(controller._store_repo, "list_with_balance", return_value=(mock_rows, 1)) as mock_list:
            rows, total = controller.list_stores(page=1, page_size=10, name="Loja", owner_name="Joao")

        mock_list.assert_called_once_with(
            page=1,
            page_size=10,
            name_filter="Loja",
            owner_filter="Joao",
        )
        assert total == 1
        assert rows == mock_rows

    def test_list_stores_without_filters(self):
        """list_stores passes None filters when not provided."""
        controller = self._make_controller()
        with patch.object(controller._store_repo, "list_with_balance", return_value=([], 0)) as mock_list:
            controller.list_stores()

        call_kwargs = mock_list.call_args[1]
        assert call_kwargs["name_filter"] is None
        assert call_kwargs["owner_filter"] is None

    def test_get_store_transactions_delegates_to_repository(self):
        """get_store_transactions returns results from the transaction repository."""
        controller = self._make_controller()
        store_id = str(uuid.uuid4())
        mock_rows = [{"id": str(uuid.uuid4()), "amount": "100.00"}]
        with patch.object(
            controller._transaction_repo,
            "list_by_store",
            return_value=(mock_rows, 1),
        ) as mock_list:
            rows, total = controller.get_store_transactions(
                store_id=store_id,
                page=2,
                page_size=5,
                type_code=1,
                nature="Entrada",
                date_from="2024-01-01",
                date_to="2024-12-31",
            )

        mock_list.assert_called_once_with(
            store_id=store_id,
            page=2,
            page_size=5,
            type_code=1,
            nature="Entrada",
            date_from="2024-01-01",
            date_to="2024-12-31",
        )
        assert total == 1
        assert rows == mock_rows

    def test_get_store_transactions_empty(self):
        """get_store_transactions returns ([], 0) when no transactions exist."""
        controller = self._make_controller()
        with patch.object(controller._transaction_repo, "list_by_store", return_value=([], 0)):
            rows, total = controller.get_store_transactions(store_id=str(uuid.uuid4()))
        assert rows == []
        assert total == 0
