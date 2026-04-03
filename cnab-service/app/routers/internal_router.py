"""API routes for internal service-to-service transaction ingestion."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.internal_controller import InternalController
from app.schemas.internal_schema import BulkTransactionRequest, BulkTransactionResponse
from app.validators.fernet_middleware import require_service_token
from cnab_shared import get_db

internal_router = APIRouter(tags=["Internal"])


@internal_router.post("/internal/transactions/", response_model=BulkTransactionResponse, status_code=201)
def receive_bulk_transactions(
    payload: BulkTransactionRequest,
    db: Session = Depends(get_db),
    _service: dict = Depends(require_service_token),
) -> BulkTransactionResponse:
    """Receives parsed transactions from upload-service and persists them.

    Authenticated via Fernet token in the X-Service-Token header.
    """
    controller = InternalController(db=db)
    result = controller.process_bulk_transactions(
        upload_id=payload.upload_id,
        transactions=[t.model_dump() for t in payload.transactions],
    )
    return BulkTransactionResponse(**result)
