"""API routes for CNAB file upload operations."""

import os

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from cnab_shared import ResourceNotFoundError, get_db

from app.controllers.upload_controller import UploadController
from app.schemas.upload_schema import UploadListResponse, UploadResponse
from app.services.file_storage import FileStorage

ALLOWED_EXTENSIONS = {".txt", ".cnab"}

upload_router = APIRouter(tags=["Uploads"])


def _get_user(request: Request) -> dict:
    """Extracts user data from request state (set by AuthMiddleware)."""
    return request.state.user


@upload_router.post("/upload/", response_model=UploadResponse, status_code=201)
def upload_cnab_file(
    request: Request,
    file: UploadFile,
    db: Session = Depends(get_db),
) -> UploadResponse:
    """Saves a CNAB file to disk and creates a pending upload record for the worker."""
    filename = file.filename or "upload.txt"
    ext = os.path.splitext(filename)[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Formato de arquivo inválido. Extensões permitidas: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = file.file.read()

    storage = FileStorage()
    file_path = storage.save(filename, content)

    user_data = _get_user(request)
    controller = UploadController(db=db, user_data=user_data)
    upload = controller.create_upload(filename=filename, file_path=file_path)

    return UploadResponse.model_validate(upload)


@upload_router.get("/uploads/", response_model=UploadListResponse)
def list_uploads(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
) -> UploadListResponse:
    """Lista os uploads do usuário autenticado com paginação."""
    user_data = _get_user(request)
    controller = UploadController(db=db, user_data=user_data)
    records, total = controller.list_uploads(page=page, page_size=page_size)

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
    """Retorna os detalhes de um upload específico pelo seu ID."""
    user_data = _get_user(request)
    controller = UploadController(db=db, user_data=user_data)
    upload = controller.get_upload(upload_id)

    if not upload:
        raise ResourceNotFoundError(f"Upload {upload_id} não encontrado.")

    return UploadResponse.model_validate(upload)
