"""API routes for transaction listing and detail."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.transaction_controller import TransactionController
from app.schemas.transaction_schema import TransactionListResponse, TransactionResponse
from cnab_shared import get_db, require_jwt

transaction_router = APIRouter(tags=["Transactions"])


@transaction_router.get("/transactions/", response_model=TransactionListResponse)
def list_transactions(
    store_id: str,
    page: int = 1,
    page_size: int = 20,
    type_codes: str | None = None,
    nature: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
) -> TransactionListResponse:
    """Returns paginated transactions for a specific store with optional filters."""
    parsed_codes: list[int] | None = None
    if type_codes:
        parsed_codes = [int(c) for c in type_codes.split(",") if c.strip().isdigit()]

    controller = TransactionController(db=db)
    return controller.list_by_store(
        store_id=store_id,
        page=page,
        page_size=page_size,
        type_codes=parsed_codes,
        nature=nature,
        date_from=date_from,
        date_to=date_to,
    )


@transaction_router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
) -> TransactionResponse:
    """Returns a single transaction by UUID."""
    controller = TransactionController(db=db)
    result = controller.get_transaction(transaction_id=transaction_id)
    if result is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Transaction not found.")
    return result
