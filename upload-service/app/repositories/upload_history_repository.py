"""Repository for upload history persistence operations."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from cnab_shared import BaseRepository

from app.models.upload_history import UploadHistory


class UploadHistoryRepository(BaseRepository[UploadHistory]):
    """Handles all database operations for UploadHistory records."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, UploadHistory)

    def list_filtered(
        self,
        user_id: int | None = None,
        status: list[str] | None = None,
        filename: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[UploadHistory], int]:
        """Filter uploads with pagination. Returns (records, total_count)."""
        query = self.db.query(UploadHistory)

        if user_id is not None:
            query = query.filter(UploadHistory.user_id == user_id)

        if status:
            query = query.filter(UploadHistory.status.in_(status))

        if filename:
            query = query.filter(UploadHistory.original_filename.ilike(f"%{filename}%"))

        if date_from:
            dt = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(UploadHistory.created_at >= dt)

        if date_to:
            dt = datetime.strptime(date_to, "%Y-%m-%d")
            query = query.filter(UploadHistory.created_at < dt + timedelta(days=1))

        total = query.count()
        records = (
            query
            .order_by(UploadHistory.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return records, total

    def get_by_user(self, user_id: int, page: int, page_size: int) -> tuple[list[UploadHistory], int]:
        """Returns paginated uploads filtered by user, plus total count."""
        query = self.db.query(UploadHistory).filter(UploadHistory.user_id == user_id)
        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(UploadHistory.created_at.desc()).offset(offset).limit(page_size).all()
        return records, total

    def get_pending(self) -> list:
        """Return all uploads with status 'pending', ordered by created_at."""
        return (
            self.db.query(self.model_class)
            .filter(self.model_class.status == "pending")
            .order_by(self.model_class.created_at.asc())
            .all()
        )

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
