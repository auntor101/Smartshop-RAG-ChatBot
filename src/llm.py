"""LLM provider factory.

Supports Groq (default - fast & free), OpenAI, and Ollama (fully local).
The active provider is selected via the ``LLM_PROVIDER`` environment variable.
"""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel

from .config import get_settings


_PLACEHOLDERS = frozenset({
    "your_groq_key_here",
    "your_openai_key_here",
})


def _is_real_key(value: str | None) -> bool:
    return bool(value) and value.strip() not in _PLACEHOLDERS


def get_llm() -> BaseChatModel:
    """Build a chat model for the configured provider."""
    settings = get_settings()
    provider = settings.llm_provider.lower()

    if provider == "groq":
        if not _is_real_key(settings.groq_api_key):
            raise ValueError(
                "GROQ_API_KEY is missing or still set to the placeholder value. "
                "Set a real key in your environment or `.env` before running the app."
            )
        from langchain_groq import ChatGroq

        return ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )

    if provider == "openai":
        if not _is_real_key(settings.openai_api_key):
            raise ValueError(
                "OPENAI_API_KEY is missing or still set to the placeholder value. "
                "Set a real key in your environment or `.env` before running the app."
            )
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=settings.temperature,
            num_predict=settings.max_tokens,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER '{provider}'. Use one of: groq, openai, ollama."
    )
