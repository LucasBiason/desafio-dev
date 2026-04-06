"""API routes for transaction type listing."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction_schema import TransactionTypeResponse
from cnab_shared import get_db, require_jwt

transaction_type_router = APIRouter(tags=["Transaction Types"])


@transaction_type_router.get("/transaction-types/", response_model=list[TransactionTypeResponse])
def list_transaction_types(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
) -> list[TransactionTypeResponse]:
    """Returns all 9 CNAB transaction type definitions."""
    repo = TransactionRepository(db=db)
    types = repo.get_all_types()
    return [
        TransactionTypeResponse(
            id=str(t.id),
            code=t.code,
            description=t.description,
            nature=t.nature,
            sign=t.sign,
        )
        for t in types
    ]
