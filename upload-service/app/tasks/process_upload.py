"""Background task that processes a CNAB upload outside the request cycle."""

from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.repositories.upload_history_repository import UploadHistoryRepository
from app.services.cnab_parser import CnabParser
from app.services.cnab_service_client import CnabServiceClient
from app.services.file_storage import FileStorage


def process_upload_task(upload_id: str, db_url: str) -> None:
    """Background task: parse CNAB file and send to cnab-service.

    Creates its own database session because background tasks run
    outside the request context and cannot reuse the request session.
    """
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        repo = UploadHistoryRepository(db)
        upload = repo.get_by_id(UUID(upload_id))
        if not upload:
            return

        repo.update_status(upload, "processing")

        try:
            storage = FileStorage()
            content = storage.read(upload.file_path)

            parser = CnabParser()
            transactions = parser.parse(content)

            client = CnabServiceClient()
            client.create_transactions(str(upload.id), transactions)

            repo.update_status(upload, "completed", total_transactions=len(transactions))
        except Exception as exc:
            repo.update_status(upload, "failed", error_message=str(exc))
    finally:
        db.close()
