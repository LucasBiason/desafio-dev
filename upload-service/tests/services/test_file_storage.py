"""Tests for FileStorage."""


from app.services.file_storage import FileStorage


class TestFileStorage:
    """Tests for FileStorage save, read, and delete operations."""

    def test_save_creates_file(self, tmp_path):
        """Save writes file content to disk and returns a valid path."""
        storage = FileStorage()
        storage.UPLOAD_DIR = tmp_path
        path = storage.save("test.txt", b"hello")
        assert tmp_path.joinpath(path.split("/")[-1]).exists()

    def test_save_uuid_prefix(self, tmp_path):
        """Saved filename has a UUID prefix prepended."""
        storage = FileStorage()
        storage.UPLOAD_DIR = tmp_path
        path = storage.save("myfile.txt", b"data")
        filename = path.split("/")[-1]
        assert filename.endswith("_myfile.txt")
        assert len(filename) > len("myfile.txt") + 1

    def test_read_returns_content(self, tmp_path):
        """Read returns the exact bytes previously written."""
        storage = FileStorage()
        storage.UPLOAD_DIR = tmp_path
        path = storage.save("read_test.txt", b"expected content")
        content = storage.read(path)
        assert content == b"expected content"

    def test_delete_removes_file(self, tmp_path):
        """Delete removes an existing file from disk."""
        storage = FileStorage()
        storage.UPLOAD_DIR = tmp_path
        path = storage.save("to_delete.txt", b"bye")
        from pathlib import Path
        assert Path(path).exists()
        storage.delete(path)
        assert not Path(path).exists()

    def test_delete_nonexistent_no_error(self, tmp_path):
        """Delete on a non-existent path does not raise an error."""
        storage = FileStorage()
        storage.UPLOAD_DIR = tmp_path
        storage.delete(str(tmp_path / "ghost_file.txt"))
