"""Small, fast keyword retriever for the bundled ShopSmart knowledge base."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from langchain_core.documents import Document

from .document_loader import load_directory
from .text_splitter import split_documents

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _score(query_terms: set[str], doc: Document) -> int:
    if not query_terms:
        return 0
    doc_terms = _tokens(doc.page_content)
    return sum(1 for term in doc_terms if term in query_terms)


@lru_cache(maxsize=4)
def _load_chunks(directory: str) -> tuple[Document, ...]:
    docs = load_directory(Path(directory))
    return tuple(split_documents(docs))


def clear_keyword_cache() -> None:
    _load_chunks.cache_clear()


class KeywordRetriever:
    """Retriever with the minimal LangChain-style ``invoke`` method we need."""

    def __init__(self, directory: str | Path, k: int) -> None:
        self.directory = str(Path(directory).resolve())
        self.k = k

    def invoke(self, query: str) -> list[Document]:
        chunks = list(_load_chunks(self.directory))
        if not chunks:
            return []

        query_terms = set(_tokens(query))
        ranked = sorted(
            enumerate(chunks),
            key=lambda item: (_score(query_terms, item[1]), -item[0]),
            reverse=True,
        )
        selected = [doc for _idx, doc in ranked[: self.k]]
        if any(_score(query_terms, doc) for doc in selected):
            return selected
        return chunks[: self.k]


def get_keyword_retriever(directory: str | Path, k: int) -> KeywordRetriever:
    return KeywordRetriever(directory, k)

