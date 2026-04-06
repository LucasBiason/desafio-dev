"""Tests for dashboard_router endpoints."""

import uuid
from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.dashboard_schema import (
    AdvancedKPIsResponse,
    AvailableFiltersResponse,
    BalanceByStoreResponse,
    DashboardSummaryResponse,
    DateRangeFilter,
    MaxExpenseDetail,
    StoreFilterItem,
    TransactionDetailItem,
    TransactionDetailResponse,
    TransactionsByHourResponse,
    TransactionsByTypeResponse,
    UploadsTimelineResponse,
)

USER_DATA = {"id": 1, "email": "user@test.com"}

AUTH_HEADER = {"Authorization": "Bearer token"}

COMMON_FILTER_PARAMS = "store_id=abc&owner_name=Joao&date_from=2024-01-01&date_to=2024-12-31"


@pytest.fixture
def auth_client():
    """Returns a TestClient with JWT auth bypassed."""
    with patch("cnab_shared.dependencies.require_jwt.UserService") as mock_user_service:
        mock_user_service.return_value.validate_token.return_value = USER_DATA
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


def _summary_response() -> DashboardSummaryResponse:
    """Returns a minimal DashboardSummaryResponse instance."""
    return DashboardSummaryResponse(
        total_stores=3,
        total_transactions=50,
        total_income=Decimal("10000.00"),
        total_expense=Decimal("4000.00"),
        overall_balance=Decimal("6000.00"),
    )


def _balance_by_store_response() -> BalanceByStoreResponse:
    """Returns a minimal BalanceByStoreResponse instance."""
    return BalanceByStoreResponse(
        labels=["Loja A", "Loja B"],
        data=[Decimal("3000.00"), Decimal("2500.00")],
    )


def _transactions_by_type_response() -> TransactionsByTypeResponse:
    """Returns a minimal TransactionsByTypeResponse instance."""
    return TransactionsByTypeResponse(
        labels=["Debito", "Credito"],
        data=[30, 20],
        colors=["#FF0000", "#00FF00"],
    )


def _uploads_timeline_response() -> UploadsTimelineResponse:
    """Returns a minimal UploadsTimelineResponse instance."""
    return UploadsTimelineResponse(
        labels=["2024-01-01", "2024-01-02"],
        data=[10, 15],
    )


def _advanced_kpis_response() -> AdvancedKPIsResponse:
    """Returns a minimal AdvancedKPIsResponse instance with a MaxExpenseDetail."""
    return AdvancedKPIsResponse(
        cash_flow=Decimal("6000.00"),
        avg_ticket=Decimal("200.00"),
        total_transactions=50,
        max_expense=MaxExpenseDetail(
            amount=Decimal("999.99"),
            store_name="Loja A",
            type_description="Debito",
            occurred_at="2024-06-15",
        ),
    )


def _transactions_by_hour_response() -> TransactionsByHourResponse:
    """Returns a minimal TransactionsByHourResponse instance."""
    return TransactionsByHourResponse(
        labels=[str(h) for h in range(24)],
        data=[i * 2 for i in range(24)],
    )


def _transaction_detail_item() -> TransactionDetailItem:
    """Returns a minimal TransactionDetailItem instance."""
    return TransactionDetailItem(
        id=str(uuid.uuid4()),
        occurred_at="2024-06-15",
        occurred_time="10:30:00",
        type_description="Debito",
        nature="Entrada",
        sign="+",
        amount=Decimal("150.00"),
        card="1234****5678",
        store_name="Loja A",
        owner_name="Joao",
        cpf="12345678901",
    )


def _transaction_detail_response(count: int = 1) -> TransactionDetailResponse:
    """Returns a minimal TransactionDetailResponse instance."""
    return TransactionDetailResponse(
        count=count,
        results=[_transaction_detail_item()] if count > 0 else [],
    )


def _available_filters_response() -> AvailableFiltersResponse:
    """Returns a minimal AvailableFiltersResponse instance."""
    return AvailableFiltersResponse(
        stores=[
            StoreFilterItem(
                id=str(uuid.uuid4()),
                name="Loja A",
                owner_name="Joao",
            )
        ],
        owners=["Joao", "Maria"],
        date_range=DateRangeFilter(min_date="2024-01-01", max_date="2024-12-31"),
    )


class TestDashboardRouter:
    """Tests for all GET /* endpoints."""

    # ------------------------------------------------------------------ #
    # GET /summary
    # ------------------------------------------------------------------ #

    def test_get_summary_returns_200(self, auth_client):
        """GET /summary returns 200 with all summary fields."""
        expected = _summary_response()
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_summary.return_value = expected
            response = auth_client.get("/summary", headers=AUTH_HEADER)

        assert response.status_code == 200
        data = response.json()
        assert data["total_stores"] == 3
        assert data["total_transactions"] == 50
        assert Decimal(data["total_income"]) == Decimal("10000.00")
        assert Decimal(data["total_expense"]) == Decimal("4000.00")
        assert Decimal(data["overall_balance"]) == Decimal("6000.00")

    def test_get_summary_with_filters(self, auth_client):
        """GET /summary passes all filter params to the controller."""
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_summary.return_value = _summary_response()
            response = auth_client.get(
                f"/summary?{COMMON_FILTER_PARAMS}",
                headers=AUTH_HEADER,
            )

        assert response.status_code == 200
        call_kwargs = mock_ctrl.return_value.get_summary.call_args[1]
        assert call_kwargs.get("store_id") == "abc"
        assert call_kwargs.get("owner_name") == "Joao"
        assert call_kwargs.get("date_from") == "2024-01-01"
        assert call_kwargs.get("date_to") == "2024-12-31"

    def test_get_summary_requires_auth(self, client):
        """GET /summary returns 401 when Authorization header is missing."""
        response = client.get("/summary")
        assert response.status_code == 401

    # ------------------------------------------------------------------ #
    # GET /balance-by-store
    # ------------------------------------------------------------------ #

    def test_get_balance_by_store_returns_200(self, auth_client):
        """GET /balance-by-store returns 200 with labels and data."""
        expected = _balance_by_store_response()
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_balance_by_store.return_value = expected
            response = auth_client.get("/balance-by-store", headers=AUTH_HEADER)

        assert response.status_code == 200
        data = response.json()
        assert data["labels"] == ["Loja A", "Loja B"]
        assert len(data["data"]) == 2

    def test_get_balance_by_store_with_filters(self, auth_client):
        """GET /balance-by-store passes all filter params to the controller."""
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_balance_by_store.return_value = _balance_by_store_response()
            response = auth_client.get(
                f"/balance-by-store?{COMMON_FILTER_PARAMS}",
                headers=AUTH_HEADER,
            )

        assert response.status_code == 200
        call_kwargs = mock_ctrl.return_value.get_balance_by_store.call_args[1]
        assert call_kwargs.get("store_id") == "abc"
        assert call_kwargs.get("owner_name") == "Joao"
        assert call_kwargs.get("date_from") == "2024-01-01"
        assert call_kwargs.get("date_to") == "2024-12-31"

    def test_get_balance_by_store_requires_auth(self, client):
        """GET /balance-by-store returns 401 without auth header."""
        response = client.get("/balance-by-store")
        assert response.status_code == 401

    # ------------------------------------------------------------------ #
    # GET /transactions-by-type
    # ------------------------------------------------------------------ #

    def test_get_transactions_by_type_returns_200(self, auth_client):
        """GET /transactions-by-type returns 200 with labels, data, colors."""
        expected = _transactions_by_type_response()
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_transactions_by_type.return_value = expected
            response = auth_client.get("/transactions-by-type", headers=AUTH_HEADER)

        assert response.status_code == 200
        data = response.json()
        assert data["labels"] == ["Debito", "Credito"]
        assert data["data"] == [30, 20]
        assert data["colors"] == ["#FF0000", "#00FF00"]

    def test_get_transactions_by_type_with_filters(self, auth_client):
        """GET /transactions-by-type passes all filter params to the controller."""
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_transactions_by_type.return_value = _transactions_by_type_response()
            response = auth_client.get(
                f"/transactions-by-type?{COMMON_FILTER_PARAMS}",
                headers=AUTH_HEADER,
            )

        assert response.status_code == 200
        call_kwargs = mock_ctrl.return_value.get_transactions_by_type.call_args[1]
        assert call_kwargs.get("store_id") == "abc"
        assert call_kwargs.get("owner_name") == "Joao"
        assert call_kwargs.get("date_from") == "2024-01-01"
        assert call_kwargs.get("date_to") == "2024-12-31"

    def test_get_transactions_by_type_requires_auth(self, client):
        """GET /transactions-by-type returns 401 without auth header."""
        response = client.get("/transactions-by-type")
        assert response.status_code == 401

    # ------------------------------------------------------------------ #
    # GET /uploads-timeline
    # ------------------------------------------------------------------ #

    def test_get_uploads_timeline_returns_200(self, auth_client):
        """GET /uploads-timeline returns 200 with labels and data."""
        expected = _uploads_timeline_response()
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_transactions_timeline.return_value = expected
            response = auth_client.get("/uploads-timeline", headers=AUTH_HEADER)

        assert response.status_code == 200
        data = response.json()
        assert data["labels"] == ["2024-01-01", "2024-01-02"]
        assert data["data"] == [10, 15]

    def test_get_uploads_timeline_with_filters(self, auth_client):
        """GET /uploads-timeline passes all filter params to the controller."""
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_transactions_timeline.return_value = _uploads_timeline_response()
            response = auth_client.get(
                f"/uploads-timeline?{COMMON_FILTER_PARAMS}",
                headers=AUTH_HEADER,
            )

        assert response.status_code == 200
        call_kwargs = mock_ctrl.return_value.get_transactions_timeline.call_args[1]
        assert call_kwargs.get("store_id") == "abc"
        assert call_kwargs.get("owner_name") == "Joao"
        assert call_kwargs.get("date_from") == "2024-01-01"
        assert call_kwargs.get("date_to") == "2024-12-31"

    def test_get_uploads_timeline_requires_auth(self, client):
        """GET /uploads-timeline returns 401 without auth header."""
        response = client.get("/uploads-timeline")
        assert response.status_code == 401

    # ------------------------------------------------------------------ #
    # GET /advanced-kpis
    # ------------------------------------------------------------------ #

    def test_get_advanced_kpis_returns_200(self, auth_client):
        """GET /advanced-kpis returns 200 with all KPI fields."""
        expected = _advanced_kpis_response()
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_advanced_kpis.return_value = expected
            response = auth_client.get("/advanced-kpis", headers=AUTH_HEADER)

        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["cash_flow"]) == Decimal("6000.00")
        assert Decimal(data["avg_ticket"]) == Decimal("200.00")
        assert data["total_transactions"] == 50
        assert data["max_expense"] is not None
        assert data["max_expense"]["store_name"] == "Loja A"

    def test_get_advanced_kpis_with_no_max_expense(self, auth_client):
        """GET /advanced-kpis returns null max_expense when there are no expenses."""
        expected = AdvancedKPIsResponse(
            cash_flow=Decimal("0.00"),
            avg_ticket=Decimal("0.00"),
            total_transactions=0,
            max_expense=None,
        )
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_advanced_kpis.return_value = expected
            response = auth_client.get("/advanced-kpis", headers=AUTH_HEADER)

        assert response.status_code == 200
        assert response.json()["max_expense"] is None

    def test_get_advanced_kpis_with_filters(self, auth_client):
        """GET /advanced-kpis passes all filter params to the controller."""
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_advanced_kpis.return_value = _advanced_kpis_response()
            response = auth_client.get(
                f"/advanced-kpis?{COMMON_FILTER_PARAMS}",
                headers=AUTH_HEADER,
            )

        assert response.status_code == 200
        call_kwargs = mock_ctrl.return_value.get_advanced_kpis.call_args[1]
        assert call_kwargs.get("store_id") == "abc"
        assert call_kwargs.get("owner_name") == "Joao"
        assert call_kwargs.get("date_from") == "2024-01-01"
        assert call_kwargs.get("date_to") == "2024-12-31"

    def test_get_advanced_kpis_requires_auth(self, client):
        """GET /advanced-kpis returns 401 without auth header."""
        response = client.get("/advanced-kpis")
        assert response.status_code == 401

    # ------------------------------------------------------------------ #
    # GET /transactions-by-hour
    # ------------------------------------------------------------------ #

    def test_get_transactions_by_hour_returns_200(self, auth_client):
        """GET /transactions-by-hour returns 200 with 24 hour labels and data."""
        expected = _transactions_by_hour_response()
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_transactions_by_hour.return_value = expected
            response = auth_client.get("/transactions-by-hour", headers=AUTH_HEADER)

        assert response.status_code == 200
        data = response.json()
        assert len(data["labels"]) == 24
        assert len(data["data"]) == 24

    def test_get_transactions_by_hour_with_filters(self, auth_client):
        """GET /transactions-by-hour passes all filter params to the controller."""
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_transactions_by_hour.return_value = _transactions_by_hour_response()
            response = auth_client.get(
                f"/transactions-by-hour?{COMMON_FILTER_PARAMS}",
                headers=AUTH_HEADER,
            )

        assert response.status_code == 200
        call_kwargs = mock_ctrl.return_value.get_transactions_by_hour.call_args[1]
        assert call_kwargs.get("store_id") == "abc"
        assert call_kwargs.get("owner_name") == "Joao"
        assert call_kwargs.get("date_from") == "2024-01-01"
        assert call_kwargs.get("date_to") == "2024-12-31"

    def test_get_transactions_by_hour_requires_auth(self, client):
        """GET /transactions-by-hour returns 401 without auth header."""
        response = client.get("/transactions-by-hour")
        assert response.status_code == 401

    # ------------------------------------------------------------------ #
    # GET /transactions-detail
    # ------------------------------------------------------------------ #

    def test_get_transactions_detail_returns_200(self, auth_client):
        """GET /transactions-detail returns 200 with count and results."""
        expected = _transaction_detail_response(count=1)
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_transactions_detail.return_value = expected
            response = auth_client.get("/transactions-detail", headers=AUTH_HEADER)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["results"]) == 1
        result = data["results"][0]
        assert result["store_name"] == "Loja A"
        assert result["owner_name"] == "Joao"
        assert result["type_description"] == "Debito"

    def test_get_transactions_detail_empty_results(self, auth_client):
        """GET /transactions-detail returns count=0 and empty results."""
        expected = _transaction_detail_response(count=0)
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_transactions_detail.return_value = expected
            response = auth_client.get("/transactions-detail", headers=AUTH_HEADER)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_get_transactions_detail_with_filters(self, auth_client):
        """GET /transactions-detail passes all filter params to the controller."""
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_transactions_detail.return_value = _transaction_detail_response(count=0)
            response = auth_client.get(
                f"/transactions-detail?{COMMON_FILTER_PARAMS}",
                headers=AUTH_HEADER,
            )

        assert response.status_code == 200
        call_kwargs = mock_ctrl.return_value.get_transactions_detail.call_args[1]
        assert call_kwargs.get("store_id") == "abc"
        assert call_kwargs.get("owner_name") == "Joao"
        assert call_kwargs.get("date_from") == "2024-01-01"
        assert call_kwargs.get("date_to") == "2024-12-31"

    def test_get_transactions_detail_with_pagination_params(self, auth_client):
        """GET /transactions-detail passes page and page_size to the controller."""
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_transactions_detail.return_value = _transaction_detail_response(count=0)
            response = auth_client.get(
                "/transactions-detail?page=3&page_size=50",
                headers=AUTH_HEADER,
            )

        assert response.status_code == 200
        call_kwargs = mock_ctrl.return_value.get_transactions_detail.call_args[1]
        assert call_kwargs.get("page") == 3
        assert call_kwargs.get("page_size") == 50

    def test_get_transactions_detail_default_pagination(self, auth_client):
        """GET /transactions-detail uses page=1 and page_size=20 by default."""
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_transactions_detail.return_value = _transaction_detail_response(count=0)
            response = auth_client.get("/transactions-detail", headers=AUTH_HEADER)

        assert response.status_code == 200
        call_kwargs = mock_ctrl.return_value.get_transactions_detail.call_args[1]
        assert call_kwargs.get("page") == 1
        assert call_kwargs.get("page_size") == 20

    def test_get_transactions_detail_requires_auth(self, client):
        """GET /transactions-detail returns 401 without auth header."""
        response = client.get("/transactions-detail")
        assert response.status_code == 401

    # ------------------------------------------------------------------ #
    # GET /available-filters
    # ------------------------------------------------------------------ #

    def test_get_available_filters_returns_200(self, auth_client):
        """GET /available-filters returns 200 with stores, owners, and date_range."""
        expected = _available_filters_response()
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_available_filters.return_value = expected
            response = auth_client.get("/available-filters", headers=AUTH_HEADER)

        assert response.status_code == 200
        data = response.json()
        assert len(data["stores"]) == 1
        assert data["stores"][0]["name"] == "Loja A"
        assert data["owners"] == ["Joao", "Maria"]
        assert data["date_range"]["min_date"] == "2024-01-01"
        assert data["date_range"]["max_date"] == "2024-12-31"

    def test_get_available_filters_empty_stores(self, auth_client):
        """GET /available-filters returns empty lists when no data exists."""
        expected = AvailableFiltersResponse(
            stores=[],
            owners=[],
            date_range=DateRangeFilter(min_date=None, max_date=None),
        )
        with patch("app.routers.dashboard_router.DashboardController") as mock_ctrl:
            mock_ctrl.return_value.get_available_filters.return_value = expected
            response = auth_client.get("/available-filters", headers=AUTH_HEADER)

        assert response.status_code == 200
        data = response.json()
        assert data["stores"] == []
        assert data["owners"] == []
        assert data["date_range"]["min_date"] is None
        assert data["date_range"]["max_date"] is None

    def test_get_available_filters_requires_auth(self, client):
        """GET /available-filters returns 401 without auth header."""
        response = client.get("/available-filters")
        assert response.status_code == 401
