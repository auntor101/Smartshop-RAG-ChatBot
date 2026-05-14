"""Tests for upload filename sanitization and size limits."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from src.config import get_settings, reset_settings
from src.ingest import ingest_uploaded_file, sanitize_upload_filename


def test_sanitize_upload_filename_strips_directories() -> None:
    assert sanitize_upload_filename(r"..\..\evil.pdf") == "evil.pdf"
    assert sanitize_upload_filename("folder/doc.txt") == "doc.txt"


def test_sanitize_upload_filename_rejects_bad() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        sanitize_upload_filename("x.exe")
    with pytest.raises(ValueError, match="Filename|Invalid"):
        sanitize_upload_filename("")


def test_ingest_upload_rejects_oversized(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "2048")
    reset_settings()
    assert get_settings().max_upload_bytes == 2048
    raw = b"x" * 3000
    with pytest.raises(ValueError, match="exceeds maximum"):
        ingest_uploaded_file("small.txt", raw, tmp_path)


@patch("src.ingest.ingest_path", return_value=3)
def test_ingest_upload_writes_safe_name(mock_ingest, tmp_path: Path) -> None:
    ingest_uploaded_file(r"sub\doc.txt", b"hello\n", tmp_path)
    assert (tmp_path / "doc.txt").exists()
    mock_ingest.assert_called_once()
