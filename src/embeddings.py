"""Embedding model factory."""

from __future__ import annotations

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from .config import get_settings


@lru_cache(maxsize=1)
def get_embeddings() -> Embeddings:
    """Return cached embeddings.

    HuggingFace sentence-transformers/all-MiniLM-L6-v2 is the default because it
    gives fast local inference, has no API cost, and performs strongly across
    multilingual support queries. OpenAI remains available as an explicit
    fallback via EMBEDDING_PROVIDER=openai.
    """
    settings = get_settings()

    if settings.embedding_provider == "openai":
        return OpenAIEmbeddings(model="text-embedding-3-small")

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
