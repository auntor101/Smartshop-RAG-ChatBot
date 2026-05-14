"""Tests for the application configuration."""

from __future__ import annotations

from pathlib import Path

from src.config import Settings, reset_settings


def test_settings_defaults(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    reset_settings()
    settings = Settings()

    assert settings.llm_provider in {"groq", "openai", "ollama"}
    assert settings.chunk_size > 0
    assert settings.chunk_overlap >= 0
    assert settings.top_k >= 1
    assert 0.0 <= settings.temperature <= 2.0
    assert settings.cors_origins == ["*"]
    assert settings.url_allowlist_hosts == []


def test_chroma_path_is_created(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "store"))
    reset_settings()
    settings = Settings()

    assert settings.chroma_path.exists()
    assert settings.chroma_path.is_dir()
