"""Business logic for CNAB upload operations."""

from sqlalchemy.orm import Session

from app.models.upload_history import UploadHistory
from app.repositories.upload_history_repository import UploadHistoryRepository
from app.services.cnab_parser import CnabParser
from app.services.cnab_service_client import CnabServiceClient
from app.services.file_storage import FileStorage


class UploadController:
    """Coordinates upload creation, listing and CNAB file processing."""

    def __init__(self, db: Session, user_data: dict) -> None:
        self.db = db
        self.user_data = user_data
        self.repository = UploadHistoryRepository(db)

    def create_upload(self, filename: str, file_path: str) -> UploadHistory:
        """Creates a new upload record with status 'pending'."""
        upload = UploadHistory(
            user_id=self.user_data.get("id"),
            original_filename=filename,
            file_path=file_path,
            status="pending",
            total_transactions=0,
        )
        return self.repository.create(upload)

    def list_uploads(self, page: int, page_size: int) -> tuple[list[UploadHistory], int]:
        """Returns the authenticated user's uploads as a paginated list."""
        user_id = self.user_data.get("id")
        return self.repository.get_by_user(user_id, page, page_size)

    def get_upload(self, upload_id: str) -> UploadHistory | None:
        """Returns a single upload record by its UUID string."""
        from uuid import UUID

        return self.repository.get_by_id(UUID(upload_id))

    def process_upload(self, upload_id: str) -> None:
        """Runs the full CNAB processing pipeline for the given upload."""
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
        except Exception as exc:
            self.repository.update_status(upload, "failed", error_message=str(exc))
