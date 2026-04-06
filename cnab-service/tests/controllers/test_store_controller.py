"""Tests for StoreController."""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.controllers.store_controller import StoreController
from app.schemas.store_schema import StoreResponse


def _store_row(name: str = "Loja A") -> dict:
    """Returns a minimal store row dict matching StoreResponse fields."""
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "owner_name": "Joao",
        "owner_cpf": "12345678901",
        "balance": Decimal("1000.00"),
        "total_income": Decimal("1500.00"),
        "total_expense": Decimal("500.00"),
        "transaction_count": 5,
    }


class TestStoreController:
    """Tests for StoreController methods."""

    def _make_controller(self) -> StoreController:
        """Creates a StoreController with a mock db session."""
        return StoreController(db=MagicMock())

    def test_list_stores_returns_store_response_objects_and_total(self):
        """list_stores converts raw rows to StoreResponse objects and returns total."""
        controller = self._make_controller()
        row = _store_row()
        with patch.object(controller._store_repo, "list_with_balance", return_value=([row], 1)):
            results, total = controller.list_stores()

        assert total == 1
        assert len(results) == 1
        assert isinstance(results[0], StoreResponse)
        assert results[0].name == "Loja A"

    def test_list_stores_passes_filters_to_repo(self):
        """list_stores forwards name and owner_name filters to the repository."""
        controller = self._make_controller()
        with patch.object(controller._store_repo, "list_with_balance", return_value=([], 0)) as mock_list:
            controller.list_stores(page=2, page_size=5, name="Loja", owner_name="Joao")

        mock_list.assert_called_once_with(
            page=2,
            page_size=5,
            name_filter="Loja",
            owner_filter="Joao",
        )

    def test_list_stores_empty_returns_empty_list_and_zero(self):
        """list_stores returns ([], 0) when the repository returns no rows."""
        controller = self._make_controller()
        with patch.object(controller._store_repo, "list_with_balance", return_value=([], 0)):
            results, total = controller.list_stores()

        assert results == []
        assert total == 0

    def test_get_store_returns_store_response_when_found(self):
        """get_store returns a StoreResponse when query_one finds the store."""
        controller = self._make_controller()
        store_id = str(uuid.uuid4())
        row = _store_row()
        with (
            patch.object(
                controller._store_repo,
                "list_with_balance",
                return_value=([row], 1),
            ),
            patch.object(
                controller._store_repo,
                "query_one",
                return_value=row,
            ),
        ):
            result = controller.get_store(store_id=store_id)

        assert isinstance(result, StoreResponse)
        assert result.name == "Loja A"

    def test_get_store_returns_none_when_not_found(self):
        """get_store returns None when query_one returns None."""
        controller = self._make_controller()
        store_id = str(uuid.uuid4())
        with (
            patch.object(
                controller._store_repo,
                "list_with_balance",
                return_value=([], 0),
            ),
            patch.object(
                controller._store_repo,
                "query_one",
                return_value=None,
            ),
        ):
            result = controller.get_store(store_id=store_id)

        assert result is None
