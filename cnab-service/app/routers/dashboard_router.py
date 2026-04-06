"""API routes for dashboard statistics endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.controllers.dashboard_controller import DashboardController
from app.dependencies import require_jwt
from app.schemas.dashboard_schema import (
    AvailableFiltersResponse,
    BalanceByStoreResponse,
    DashboardSummaryResponse,
    TransactionsByTypeResponse,
    UploadsTimelineResponse,
)
from cnab_shared import get_db

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


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


@dashboard_router.get("/available-filters", response_model=AvailableFiltersResponse)
def get_available_filters(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
) -> AvailableFiltersResponse:
    """Returns stores, owner names and date range for populating frontend filter dropdowns."""
    return DashboardController(db=db).get_available_filters()
