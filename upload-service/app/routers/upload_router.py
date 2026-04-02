"""API routes for CNAB file upload operations."""

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from cnab_shared import ResourceNotFoundError, get_db

from app.controllers.upload_controller import UploadController
from app.schemas.upload_schema import UploadListResponse, UploadResponse

upload_router = APIRouter(tags=["Uploads"])


def _get_user(request: Request) -> dict:
    return request.state.user


@upload_router.post("/upload/", response_model=UploadResponse, status_code=201)
def upload_cnab_file(
    request: Request,
    file: UploadFile,
    db: Session = Depends(get_db),
) -> UploadResponse:
    """Receives a CNAB file, validates, stores, and queues for background processing."""
    user_data = _get_user(request)
    filename = file.filename or "upload.txt"
    content = file.file.read()

    controller = UploadController(db=db, user_data=user_data)
    upload = controller.create_upload(filename=filename, content=content)

    return UploadResponse.model_validate(upload)


@upload_router.get("/uploads/", response_model=UploadListResponse)
def list_uploads(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    filename: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: Session = Depends(get_db),
) -> UploadListResponse:
    """Lists authenticated user's uploads with optional filters and pagination."""
    user_data = _get_user(request)
    controller = UploadController(db=db, user_data=user_data)

    status_list = [s.strip() for s in status.split(",")] if status else None

    records, total = controller.list_uploads(
        page=page,
        page_size=page_size,
        status=status_list,
        filename=filename,
        date_from=date_from,
        date_to=date_to,
    )

    return UploadListResponse(
        count=total,
        results=[UploadResponse.model_validate(r) for r in records],
    )


@upload_router.get("/uploads/{upload_id}", response_model=UploadResponse)
def get_upload(
    upload_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> UploadResponse:
    """Returns details of a specific upload by ID."""
    user_data = _get_user(request)
    controller = UploadController(db=db, user_data=user_data)
    upload = controller.get_upload(upload_id)

    if not upload:
        raise ResourceNotFoundError(f"Upload {upload_id} not found.")

    return UploadResponse.model_validate(upload)
