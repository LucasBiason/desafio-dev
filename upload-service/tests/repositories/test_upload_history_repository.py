"""Tests for UploadHistoryRepository."""

import pytest
from datetime import datetime, timedelta

from app.models.upload_history import UploadHistory
from app.repositories.upload_history_repository import UploadHistoryRepository


def _make_upload(db, filename="test.txt", status="pending", user_id=1, created_at=None):
    """Helper to create and persist an UploadHistory record."""
    upload = UploadHistory()
    upload.user_id = user_id
    upload.original_filename = filename
    upload.file_path = f"/uploads/{filename}"
    upload.status = status
    upload.total_transactions = 0
    if created_at:
        upload.created_at = created_at
    db.add(upload)
    db.commit()
    db.refresh(upload)
    return upload


class TestUploadHistoryRepository:
    """Tests for UploadHistoryRepository CRUD and filtering methods."""

    def test_create_and_get_by_id(self, db):
        """Created record can be retrieved by its UUID."""
        upload = _make_upload(db)
        repo = UploadHistoryRepository(db)
        found = repo.get_by_id(upload.id)
        assert found is not None
        assert found.id == upload.id
        assert found.original_filename == "test.txt"

    def test_list_filtered_by_status(self, db):
        """list_filtered returns only records matching the given status list."""
        _make_upload(db, filename="a.txt", status="pending")
        _make_upload(db, filename="b.txt", status="completed")
        repo = UploadHistoryRepository(db)
        records, total = repo.list_filtered(status=["pending"])
        assert total == 1
        assert records[0].status == "pending"

    def test_list_filtered_by_filename(self, db):
        """list_filtered returns only records whose filename matches the pattern."""
        _make_upload(db, filename="invoice.txt")
        _make_upload(db, filename="other.txt")
        repo = UploadHistoryRepository(db)
        records, total = repo.list_filtered(filename="invoice")
        assert total == 1
        assert "invoice" in records[0].original_filename

    def test_list_filtered_by_date(self, db):
        """list_filtered date_from and date_to narrow down results correctly."""
        yesterday = datetime.now() - timedelta(days=1)
        _make_upload(db, filename="old.txt", created_at=yesterday)
        _make_upload(db, filename="new.txt")
        repo = UploadHistoryRepository(db)
        today_str = datetime.now().strftime("%Y-%m-%d")
        records, total = repo.list_filtered(date_from=today_str)
        assert total >= 1
        for r in records:
            assert r.original_filename != "old.txt"

    def test_list_filtered_pagination(self, db):
        """list_filtered respects page and page_size parameters."""
        for i in range(5):
            _make_upload(db, filename=f"file_{i}.txt")
        repo = UploadHistoryRepository(db)
        records, total = repo.list_filtered(page=1, page_size=2)
        assert total == 5
        assert len(records) == 2

    def test_get_pending(self, db):
        """get_pending returns only records with status 'pending'."""
        _make_upload(db, filename="pending.txt", status="pending")
        _make_upload(db, filename="done.txt", status="completed")
        repo = UploadHistoryRepository(db)
        pending = repo.get_pending()
        assert len(pending) == 1
        assert pending[0].status == "pending"

    def test_update_status(self, db):
        """update_status changes the status field and persists it."""
        upload = _make_upload(db, status="pending")
        repo = UploadHistoryRepository(db)
        updated = repo.update_status(upload, "completed", total_transactions=5)
        assert updated.status == "completed"
        assert updated.total_transactions == 5

    def test_update_status_with_error(self, db):
        """update_status sets error_message when provided."""
        upload = _make_upload(db, status="pending")
        repo = UploadHistoryRepository(db)
        updated = repo.update_status(upload, "failed", error_message="something went wrong")
        assert updated.status == "failed"
        assert updated.error_message == "something went wrong"

    def test_list_filtered_by_user_id(self, db):
        """list_filtered returns only records belonging to the given user_id."""
        _make_upload(db, filename="user1.txt", user_id=1)
        _make_upload(db, filename="user2.txt", user_id=2)
        repo = UploadHistoryRepository(db)
        records, total = repo.list_filtered(user_id=1)
        assert total == 1
        assert records[0].user_id == 1

    def test_list_filtered_by_date_to(self, db):
        """list_filtered date_to excludes records created after the given date."""
        _make_upload(db, filename="recent.txt")
        repo = UploadHistoryRepository(db)
        past_str = "2000-01-01"
        records, total = repo.list_filtered(date_to=past_str)
        assert total == 0

    def test_get_by_user(self, db):
        """get_by_user returns paginated uploads for the specified user."""
        _make_upload(db, filename="u1.txt", user_id=10)
        _make_upload(db, filename="u2.txt", user_id=10)
        _make_upload(db, filename="other.txt", user_id=99)
        repo = UploadHistoryRepository(db)
        records, total = repo.get_by_user(user_id=10, page=1, page_size=10)
        assert total == 2
        assert len(records) == 2
        assert all(r.user_id == 10 for r in records)

    def test_upload_history_repr(self, db):
        """UploadHistory __repr__ returns a string with id, filename and status."""
        upload = _make_upload(db, filename="repr_test.txt", status="pending")
        text = repr(upload)
        assert "repr_test.txt" in text
        assert "pending" in text
