"""API routes for store listing and transaction queries."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.store_controller import StoreController
from app.dependencies import require_jwt
from app.schemas.store_schema import StoreListResponse, StoreResponse
from app.schemas.transaction_schema import TransactionListResponse, TransactionResponse, TransactionTypeResponse
from cnab_shared import get_db

store_router = APIRouter(tags=["Stores"])


def _build_transaction_response(row: dict) -> TransactionResponse:
    """Converts a raw SQL result row into a TransactionResponse."""
    transaction_type = TransactionTypeResponse(
        id=row["transaction_type_id"],
        code=row["transaction_type_code"],
        description=row["transaction_type_description"],
        nature=row["transaction_type_nature"],
        sign=row["transaction_type_sign"],
    )
    store_dict = {
        "id": row["store_id"],
        "name": row["store_name"],
        "owner_name": row["store_owner_name"],
        "owner_cpf": row["store_owner_cpf"],
    }
    return TransactionResponse(
        id=row["id"],
        transaction_type=transaction_type,
        amount=row["amount"],
        card=row["card"],
        occurred_at=str(row["occurred_at"]),
        occurred_time=str(row["occurred_time"]),
        store=store_dict,
    )


@store_router.get("/stores/", response_model=StoreListResponse)
def list_stores(
    page: int = 1,
    page_size: int = 20,
    name: str | None = None,
    owner_name: str | None = None,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
) -> StoreListResponse:
    """Returns paginated stores with computed balance, income and expense totals."""
    controller = StoreController(db=db)
    rows, total = controller.list_stores(
        page=page,
        page_size=page_size,
        name=name,
        owner_name=owner_name,
    )
    results = [StoreResponse(**row) for row in rows]
    return StoreListResponse(count=total, results=results)


@store_router.get("/stores/{store_id}/transactions/", response_model=TransactionListResponse)
def list_store_transactions(
    store_id: str,
    page: int = 1,
    page_size: int = 20,
    type_code: int | None = None,
    nature: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
) -> TransactionListResponse:
    """Returns paginated transactions for a specific store with optional filters."""
    controller = StoreController(db=db)
    rows, total = controller.get_store_transactions(
        store_id=store_id,
        page=page,
        page_size=page_size,
        type_code=type_code,
        nature=nature,
        date_from=date_from,
        date_to=date_to,
    )
    results = [_build_transaction_response(row) for row in rows]
    return TransactionListResponse(count=total, results=results)
