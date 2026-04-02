"""Worker that processes pending CNAB uploads."""

import logging
import os
import signal
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.repositories.upload_history_repository import UploadHistoryRepository
from app.services.cnab_parser import CnabParser
from app.services.cnab_service_client import CnabServiceClient
from app.services.file_storage import FileStorage

logger = logging.getLogger(__name__)

POLL_INTERVAL = int(os.environ.get("WORKER_POLL_INTERVAL", "10"))

running = True


def handle_signal(signum, frame):
    global running
    logger.info("Received signal %s, shutting down...", signum)
    running = False


signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)


def process_single_upload(db, upload):
    """Process one upload: parse file and send to cnab-service."""
    repo = UploadHistoryRepository(db)
    repo.update_status(upload, "processing")

    try:
        storage = FileStorage()
        content = storage.read(upload.file_path)

        parser = CnabParser()
        transactions = parser.parse(content)

        client = CnabServiceClient()
        client.create_transactions(str(upload.id), transactions)

        repo.update_status(upload, "completed", total_transactions=len(transactions))
        logger.info("Upload %s completed: %d transactions", upload.id, len(transactions))
    except Exception as exc:
        repo.update_status(upload, "failed", error_message=str(exc))
        logger.error("Upload %s failed: %s", upload.id, exc)


def run():
    """Main worker loop."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set")
        return

    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)

    logger.info("Worker started (polling every %ds)", POLL_INTERVAL)

    while running:
        db = SessionLocal()
        try:
            repo = UploadHistoryRepository(db)
            pending = repo.get_pending()

            if pending:
                logger.info("Found %d pending upload(s)", len(pending))
                for upload in pending:
                    process_single_upload(db, upload)
        except Exception as exc:
            logger.error("Worker error: %s", exc)
        finally:
            db.close()

        for _ in range(POLL_INTERVAL):
            if not running:
                break
            time.sleep(1)

    logger.info("Worker stopped.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )
    run()
