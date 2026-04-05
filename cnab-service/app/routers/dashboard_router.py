"""API routes for dashboard statistics endpoints."""

from fastapi import APIRouter, Depends
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
) -> DashboardSummaryResponse:
    """Returns overall counts and financial totals across all stores."""
    return DashboardController(db=db).get_summary()


@dashboard_router.get("/balance-by-store", response_model=BalanceByStoreResponse)
def get_balance_by_store(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
) -> BalanceByStoreResponse:
    """Returns per-store balance data suitable for bar chart rendering."""
    return DashboardController(db=db).get_balance_by_store()


@dashboard_router.get("/transactions-by-type", response_model=TransactionsByTypeResponse)
def get_transactions_by_type(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
) -> TransactionsByTypeResponse:
    """Returns transaction count per type with colors for pie/donut chart rendering."""
    return DashboardController(db=db).get_transactions_by_type()


@dashboard_router.get("/uploads-timeline", response_model=UploadsTimelineResponse)
def get_uploads_timeline(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
) -> UploadsTimelineResponse:
    """Returns transaction count grouped by date for line chart rendering."""
    return DashboardController(db=db).get_transactions_timeline()
