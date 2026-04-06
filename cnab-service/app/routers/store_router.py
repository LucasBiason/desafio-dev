"""API routes for store listing and detail."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.store_controller import StoreController
from app.schemas.store_schema import StoreListResponse, StoreResponse
from cnab_shared import get_db, require_jwt

store_router = APIRouter(tags=["Stores"])


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
    results, total = controller.list_stores(
        page=page,
        page_size=page_size,
        name=name,
        owner_name=owner_name,
    )
    return StoreListResponse(count=total, results=results)


@store_router.get("/stores/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: str,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_jwt),
) -> StoreResponse:
    """Returns a single store with balance data."""
    controller = StoreController(db=db)
    result = controller.get_store(store_id=store_id)
    if result is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Store not found.")
    return result
