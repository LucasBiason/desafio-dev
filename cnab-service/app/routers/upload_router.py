"""API routes for upload service transaction ingestion."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.upload_controller import UploadController
from app.schemas.upload_schema import BulkTransactionRequest, BulkTransactionResponse
from cnab_shared import get_db, require_service_token

upload_router = APIRouter(tags=["Upload"])


@upload_router.post("/transactions/upload/", response_model=BulkTransactionResponse, status_code=201)
def receive_bulk_transactions(
    payload: BulkTransactionRequest,
    db: Session = Depends(get_db),
    _service: dict = Depends(require_service_token),
) -> BulkTransactionResponse:
    """Receives parsed transactions from upload-service and persists them.

    Authenticated via Fernet token in the X-Service-Token header.
    """
    controller = UploadController(db=db)
    result = controller.process_bulk_transactions(
        upload_id=payload.upload_id,
        transactions=[t.model_dump() for t in payload.transactions],
    )
    return BulkTransactionResponse(**result)
