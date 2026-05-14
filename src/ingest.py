"""High-level ingestion helpers: file/URL -> chunks -> vector store."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

from langchain_core.documents import Document

from .config import get_settings
from .document_loader import (
    SUPPORTED_EXTENSIONS,
    load_directory,
    load_file,
    load_urls,
)
from .text_splitter import split_documents
from .vector_store import add_documents

logger = logging.getLogger(__name__)


def sanitize_upload_filename(filename: str) -> str:
    """Return a single-segment safe filename; raise ValueError if invalid."""
    if not filename or not str(filename).strip():
        raise ValueError("Filename is required.")
    base = Path(filename).name
    if not base or base in {".", ".."}:
        raise ValueError("Invalid filename.")
    if "\x00" in base:
        raise ValueError("Invalid filename.")
    suffix = Path(base).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file '{filename}'. Allowed: {sorted(SUPPORTED_EXTENSIONS)}"
        )
    return base


def ingest_path(path: str | Path) -> int:
    """Ingest a single file or an entire directory."""
    path = Path(path)
    if path.is_dir():
        docs = load_directory(path)
    else:
        docs = load_file(path)
    return _persist(docs)


def ingest_urls(urls: Iterable[str]) -> int:
    """Ingest a list of URLs."""
    docs = load_urls(urls)
    return _persist(docs)


def ingest_uploaded_file(filename: str, raw_bytes: bytes, save_dir: str | Path) -> int:
    """Persist an uploaded file to disk, then ingest it.

    Useful for the Streamlit UI where users upload via ``st.file_uploader``.
    """
    settings = get_settings()
    if len(raw_bytes) > settings.max_upload_bytes:
        raise ValueError(
            f"File exceeds maximum size of {settings.max_upload_bytes} bytes."
        )

    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_upload_filename(filename)
    save_resolved = save_dir.resolve()
    file_path = (save_resolved / safe_name).resolve()
    try:
        file_path.relative_to(save_resolved)
    except ValueError as exc:
        raise ValueError("Invalid file path.") from exc

    file_path.write_bytes(raw_bytes)
    return ingest_path(file_path)


def _persist(documents: list[Document]) -> int:
    if not documents:
        logger.warning("Ingestion produced no documents.")
        return 0
    chunks = split_documents(documents)
    logger.info("Split %d docs into %d chunks.", len(documents), len(chunks))
    return add_documents(chunks)
