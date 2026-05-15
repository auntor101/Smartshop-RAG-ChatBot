"""Embedding model factory."""

from __future__ import annotations

import os

# See app.py: same Windows + Streamlit stderr issue when tqdm loads with transformers.
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from .config import get_settings


@lru_cache(maxsize=1)
def get_embeddings() -> Embeddings:
    """Return cached embeddings.

    ``sentence-transformers/all-MiniLM-L6-v2`` is the default: fast local inference,
    no embedding API cost, and solid general-purpose quality. OpenAI embeddings stay
    available via ``EMBEDDING_PROVIDER=openai``.
    """
    settings = get_settings()

    if settings.embedding_provider == "openai":
        return OpenAIEmbeddings(model="text-embedding-3-small")

    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True, "batch_size": 64},
    )
