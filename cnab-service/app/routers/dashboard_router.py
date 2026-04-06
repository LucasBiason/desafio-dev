"""API routes for dashboard statistics endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.controllers.dashboard_controller import DashboardController
from app.dependencies import require_jwt
from app.schemas.dashboard_schema import (
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
    year: int | None = Query(default=None, description="Filter by year (e.g. 2019)"),
    month: int | None = Query(default=None, ge=1, le=12, description="Filter by month (1-12); requires year"),
) -> DashboardSummaryResponse:
    """Returns overall counts and financial totals across all stores."""
    return DashboardController(db=db).get_summary(year=year, month=month)


@dashboard_router.get("/balance-by-store", response_model=BalanceByStoreResponse)
def get_balance_by_store(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
    year: int | None = Query(default=None, description="Filter by year (e.g. 2019)"),
    month: int | None = Query(default=None, ge=1, le=12, description="Filter by month (1-12); requires year"),
) -> BalanceByStoreResponse:
    """Returns per-store balance data suitable for bar chart rendering."""
    return DashboardController(db=db).get_balance_by_store(year=year, month=month)


@dashboard_router.get("/transactions-by-type", response_model=TransactionsByTypeResponse)
def get_transactions_by_type(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
    year: int | None = Query(default=None, description="Filter by year (e.g. 2019)"),
    month: int | None = Query(default=None, ge=1, le=12, description="Filter by month (1-12); requires year"),
) -> TransactionsByTypeResponse:
    """Returns transaction count per type with colors for pie/donut chart rendering."""
    return DashboardController(db=db).get_transactions_by_type(year=year, month=month)


@dashboard_router.get("/uploads-timeline", response_model=UploadsTimelineResponse)
def get_uploads_timeline(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
    year: int | None = Query(default=None, description="Filter by year (e.g. 2019)"),
    month: int | None = Query(default=None, ge=1, le=12, description="Filter by month (1-12); requires year"),
) -> UploadsTimelineResponse:
    """Returns transaction count grouped by date for line chart rendering."""
    return DashboardController(db=db).get_transactions_timeline(year=year, month=month)
