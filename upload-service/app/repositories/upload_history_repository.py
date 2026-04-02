"""Repository for upload history persistence operations."""

from sqlalchemy.orm import Session

from cnab_shared import BaseRepository

from app.models.upload_history import UploadHistory


class UploadHistoryRepository(BaseRepository[UploadHistory]):
    """Handles all database operations for UploadHistory records."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, UploadHistory)

    def get_by_user(self, user_id: int, page: int, page_size: int) -> tuple[list[UploadHistory], int]:
        """Returns paginated uploads filtered by user, plus total count."""
        query = self.db.query(UploadHistory).filter(UploadHistory.user_id == user_id)
        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(UploadHistory.created_at.desc()).offset(offset).limit(page_size).all()
        return records, total

    def update_status(
        self,
        upload: UploadHistory,
        status: str,
        error_message: str | None = None,
        total_transactions: int | None = None,
    ) -> UploadHistory:
        """Updates status fields on an upload record and persists the changes."""
        upload.status = status
        if error_message is not None:
            upload.error_message = error_message
        if total_transactions is not None:
            upload.total_transactions = total_transactions
        self.db.commit()
        self.db.refresh(upload)
        return upload
