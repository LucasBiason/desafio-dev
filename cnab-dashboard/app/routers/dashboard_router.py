"""API routes for dashboard statistics endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.controllers.dashboard_controller import DashboardController
from app.schemas.dashboard_schema import (
    AdvancedKPIsResponse,
    AvailableFiltersResponse,
    BalanceByStoreResponse,
    DashboardSummaryResponse,
    TransactionDetailResponse,
    TransactionsByHourResponse,
    TransactionsByTypeResponse,
    UploadsTimelineResponse,
)
from cnab_shared import get_db, require_jwt

dashboard_router = APIRouter(tags=["Dashboard"])


@dashboard_router.get("/summary", response_model=DashboardSummaryResponse)
def get_summary(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
    store_id: str | None = Query(default=None, description="Filter by store UUID"),
    owner_name: str | None = Query(default=None, description="Filter by owner name (partial match)"),
    date_from: str | None = Query(default=None, description="Start date filter (YYYY-MM-DD)"),
    date_to: str | None = Query(default=None, description="End date filter (YYYY-MM-DD)"),
) -> DashboardSummaryResponse:
    """Returns overall counts and financial totals across all stores."""
    return DashboardController(db=db).get_summary(
        store_id=store_id,
        owner_name=owner_name,
        date_from=date_from,
        date_to=date_to,
    )


@dashboard_router.get("/balance-by-store", response_model=BalanceByStoreResponse)
def get_balance_by_store(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
    store_id: str | None = Query(default=None, description="Filter by store UUID"),
    owner_name: str | None = Query(default=None, description="Filter by owner name (partial match)"),
    date_from: str | None = Query(default=None, description="Start date filter (YYYY-MM-DD)"),
    date_to: str | None = Query(default=None, description="End date filter (YYYY-MM-DD)"),
) -> BalanceByStoreResponse:
    """Returns per-store balance data suitable for bar chart rendering."""
    return DashboardController(db=db).get_balance_by_store(
        store_id=store_id,
        owner_name=owner_name,
        date_from=date_from,
        date_to=date_to,
    )


@dashboard_router.get("/transactions-by-type", response_model=TransactionsByTypeResponse)
def get_transactions_by_type(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
    store_id: str | None = Query(default=None, description="Filter by store UUID"),
    owner_name: str | None = Query(default=None, description="Filter by owner name (partial match)"),
    date_from: str | None = Query(default=None, description="Start date filter (YYYY-MM-DD)"),
    date_to: str | None = Query(default=None, description="End date filter (YYYY-MM-DD)"),
) -> TransactionsByTypeResponse:
    """Returns transaction count per type with colors for pie/donut chart rendering."""
    return DashboardController(db=db).get_transactions_by_type(
        store_id=store_id,
        owner_name=owner_name,
        date_from=date_from,
        date_to=date_to,
    )


@dashboard_router.get("/uploads-timeline", response_model=UploadsTimelineResponse)
def get_uploads_timeline(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
    store_id: str | None = Query(default=None, description="Filter by store UUID"),
    owner_name: str | None = Query(default=None, description="Filter by owner name (partial match)"),
    date_from: str | None = Query(default=None, description="Start date filter (YYYY-MM-DD)"),
    date_to: str | None = Query(default=None, description="End date filter (YYYY-MM-DD)"),
) -> UploadsTimelineResponse:
    """Returns transaction count grouped by date for line chart rendering."""
    return DashboardController(db=db).get_transactions_timeline(
        store_id=store_id,
        owner_name=owner_name,
        date_from=date_from,
        date_to=date_to,
    )


@dashboard_router.get("/advanced-kpis", response_model=AdvancedKPIsResponse)
def get_advanced_kpis(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
    store_id: str | None = Query(default=None, description="Filter by store UUID"),
    owner_name: str | None = Query(default=None, description="Filter by owner name (partial match)"),
    date_from: str | None = Query(default=None, description="Start date filter (YYYY-MM-DD)"),
    date_to: str | None = Query(default=None, description="End date filter (YYYY-MM-DD)"),
) -> AdvancedKPIsResponse:
    """Returns advanced KPI metrics: cash flow, average ticket, total transactions and max expense."""
    return DashboardController(db=db).get_advanced_kpis(
        store_id=store_id,
        owner_name=owner_name,
        date_from=date_from,
        date_to=date_to,
    )


@dashboard_router.get("/transactions-by-hour", response_model=TransactionsByHourResponse)
def get_transactions_by_hour(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
    store_id: str | None = Query(default=None, description="Filter by store UUID"),
    owner_name: str | None = Query(default=None, description="Filter by owner name (partial match)"),
    date_from: str | None = Query(default=None, description="Start date filter (YYYY-MM-DD)"),
    date_to: str | None = Query(default=None, description="End date filter (YYYY-MM-DD)"),
) -> TransactionsByHourResponse:
    """Returns transaction count per hour of day (all 24 hours, missing hours filled with 0)."""
    return DashboardController(db=db).get_transactions_by_hour(
        store_id=store_id,
        owner_name=owner_name,
        date_from=date_from,
        date_to=date_to,
    )


@dashboard_router.get("/transactions-detail", response_model=TransactionDetailResponse)
def get_transactions_detail(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
    store_id: str | None = Query(default=None, description="Filter by store UUID"),
    owner_name: str | None = Query(default=None, description="Filter by owner name (partial match)"),
    date_from: str | None = Query(default=None, description="Start date filter (YYYY-MM-DD)"),
    date_to: str | None = Query(default=None, description="End date filter (YYYY-MM-DD)"),
    nature: str | None = Query(default=None, description="Filter by nature: entrada or saida"),
    ordering: str | None = Query(default=None, description="Sort field, prefix with - for desc (e.g. -amount)"),
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=20, ge=1, le=200, description="Results per page"),
) -> TransactionDetailResponse:
    """Returns a paginated list of transaction detail rows for the drill-down table."""
    return DashboardController(db=db).get_transactions_detail(
        store_id=store_id,
        owner_name=owner_name,
        date_from=date_from,
        date_to=date_to,
        nature=nature,
        ordering=ordering,
        page=page,
        page_size=page_size,
    )


@dashboard_router.get("/available-filters", response_model=AvailableFiltersResponse)
def get_available_filters(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
) -> AvailableFiltersResponse:
    """Returns stores, owner names and date range for populating frontend filter dropdowns."""
    return DashboardController(db=db).get_available_filters()
