"""Worker entry point — starts the polling loop for background processing."""

import logging
import os
import signal
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.tasks.process_upload import process_pending_uploads

logger = logging.getLogger(__name__)

POLL_INTERVAL = int(os.environ.get("WORKER_POLL_INTERVAL", "10"))
_running = True


def _handle_signal(signum, _frame):
    global _running
    logger.info("Signal %s received, stopping...", signum)
    _running = False


def _sleep(seconds: int) -> None:
    """Interruptible sleep for graceful shutdown."""
    for _ in range(seconds):
        if not _running:
            break
        time.sleep(1)


def run() -> None:
    """Initialize DB connection and start the polling loop."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set")
        return

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    logger.info("Worker started (polling every %ds)", POLL_INTERVAL)

    while _running:
        db = Session()
        try:
            process_pending_uploads(db)
        except Exception as exc:
            logger.error("Worker cycle error: %s", exc)
        finally:
            db.close()
        _sleep(POLL_INTERVAL)

    logger.info("Worker stopped.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )
    run()
