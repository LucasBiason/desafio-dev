"""Business logic for CNAB upload operations."""

import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.upload_history import UploadHistory
from app.repositories.upload_history_repository import UploadHistoryRepository
from app.services.cnab_parser import CnabParser
from app.services.cnab_service_client import CnabServiceClient
from app.services.file_storage import FileStorage
from app.validators.upload_validator import UploadValidator

logger = logging.getLogger(__name__)


class UploadController:
    """Upload validation, file storage, and processing lifecycle."""

    def __init__(self, db: Session, user_data: dict) -> None:
        self.db = db
        self.user_data = user_data
        self.repository = UploadHistoryRepository(db)

    def create_upload(self, filename: str, content: bytes) -> UploadHistory:
        """Validate file, store on disk, create pending record. Returns immediately."""
        # 1. Validate
        result = UploadValidator.validate_file(filename, content)
        if not result["valid"]:
            raise HTTPException(status_code=422, detail=result["error"])

        # 2. Store file
        storage = FileStorage()
        file_path = storage.save(filename, content)

        # 3. Create record (worker picks it up)
        upload = UploadHistory()
        upload.user_id = self.user_data.get("id")
        upload.original_filename = filename
        upload.file_path = file_path
        upload.status = "pending"
        upload.total_transactions = 0

        return self.repository.create(upload)

    def list_uploads(
        self,
        page: int = 1,
        page_size: int = 20,
        status: list[str] | None = None,
        filename: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[UploadHistory], int]:
        """Returns filtered and paginated uploads for the current user."""
        user_id = self.user_data.get("id")
        return self.repository.list_filtered(
            user_id=user_id,
            status=status,
            filename=filename,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
        )

    def get_upload(self, upload_id: str) -> UploadHistory | None:
        """Returns a single upload by UUID."""
        return self.repository.get_by_id(UUID(upload_id))

    def process_upload(self, upload_id: str) -> None:
        """Runs the CNAB processing pipeline. Called by the worker."""
        upload = self.get_upload(upload_id)
        if not upload:
            return

        self.repository.update_status(upload, "processing")

        try:
            storage = FileStorage()
            content = storage.read(upload.file_path)

            parser = CnabParser()
            transactions = parser.parse(content)

            client = CnabServiceClient()
            client.create_transactions(str(upload.id), transactions)

            self.repository.update_status(upload, "completed", total_transactions=len(transactions))
            logger.info("Upload %s completed: %d transactions", upload.id, len(transactions))
        except Exception as exc:
            self.repository.update_status(upload, "failed", error_message=str(exc))
            logger.error("Upload %s failed: %s", upload.id, exc)
