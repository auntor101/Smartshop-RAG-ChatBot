"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file so the app works regardless of CWD
# (local `streamlit run app.py`, pytest from any dir, or Streamlit Cloud).
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Centralised, type-safe application settings."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- LLM provider ----
    llm_provider: Literal["groq", "openai", "ollama"] = Field(
        default="groq", description="Which LLM backend to use."
    )

    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # ---- Embeddings ----
    embedding_provider: Literal["huggingface", "openai"] = "huggingface"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ---- Vector store ----
    chroma_persist_dir: str = "./chroma_db"
    collection_name: str = "shopsmart_support"

    # ---- RAG hyperparameters ----
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 4
    temperature: float = 0.2
    max_tokens: int = 1024

    # ---- Security / deployment ----
    admin_password: str | None = Field(
        default=None,
        description="If set, Streamlit admin actions require this password.",
    )
    api_token: str | None = Field(
        default=None,
        description="If set, FastAPI protects ingest/reset/status with Bearer token.",
    )
    enable_public_admin: bool = Field(
        default=True,
        description=(
            "If False, Streamlit hides KB load, uploads, URL ingest, and reset "
            "(chat-only public UI)."
        ),
    )
    auto_ingest_on_startup: bool = Field(
        default=False,
        description=(
            "If True, Streamlit indexes the bundled KB before first render. "
            "Keep False on Streamlit Cloud so cold starts do not time out."
        ),
    )
    allowed_origins: str = Field(
        default="",
        description="Comma-separated CORS origins; empty means allow all (*).",
    )
    max_upload_bytes: int = Field(
        default=20 * 1024 * 1024,
        ge=1024,
        description="Maximum uploaded file size for ingestion.",
    )
    max_url_fetch_bytes: int = Field(
        default=10 * 1024 * 1024,
        ge=1024,
        description="Maximum downloaded bytes when ingesting a URL.",
    )
    max_url_redirects: int = Field(default=5, ge=0, le=20)
    url_fetch_timeout_seconds: int = Field(default=30, ge=5, le=120)
    url_allowlist: str = Field(
        default="",
        description=(
            "Comma-separated hostname allowlist for URL ingestion; "
            "empty means only scheme/DNS/IP safety checks apply."
        ),
    )

    @property
    def chroma_path(self) -> Path:
        path = Path(self.chroma_persist_dir).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def cors_origins(self) -> list[str]:
        raw = (self.allowed_origins or "").strip()
        if not raw:
            return ["*"]
        parts = [o.strip() for o in raw.split(",") if o.strip()]
        return parts if parts else ["*"]

    @property
    def url_allowlist_hosts(self) -> list[str]:
        raw = (self.url_allowlist or "").strip()
        if not raw:
            return []
        return [h.strip().lower() for h in raw.split(",") if h.strip()]


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return a cached `Settings` instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Clear cached settings (for tests and reload after env changes)."""
    global _settings
    _settings = None
