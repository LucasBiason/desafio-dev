"""Task that finds and processes pending CNAB uploads."""

import logging

from sqlalchemy.orm import Session

from app.controllers.upload_controller import UploadController
from app.repositories.upload_history_repository import UploadHistoryRepository

logger = logging.getLogger(__name__)


def process_pending_uploads(db: Session) -> None:
    """Finds all pending uploads and processes each one via the controller."""
    pending = UploadHistoryRepository(db).get_pending()

    if not pending:
        return

    logger.info("Found %d pending upload(s)", len(pending))
    controller = UploadController(db=db, user_data={})

    for upload in pending:
        controller.process_upload(str(upload.id))
