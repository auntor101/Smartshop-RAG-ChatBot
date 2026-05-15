"""API smoke tests using FastAPI's in-process TestClient.

These tests exercise every endpoint that does NOT require an LLM call, plus a
mocked /chat to verify request/response wiring without spending API credits.
"""

from __future__ import annotations

from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app, get_chatbot
from src.rag_chain import RAGResponse


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_redirects_to_docs(client: TestClient) -> None:
    response = client.get("/", follow_redirects=False)
    assert response.status_code in {307, 308}
    assert response.headers["location"] == "/docs"


def test_status_returns_config(client: TestClient) -> None:
    response = client.get("/status")
    assert response.status_code == 200

    body = response.json()
    assert body["provider"] in {"groq", "openai", "ollama"}
    assert body["chunk_size"] > 0
    assert body["chunk_overlap"] >= 0
    assert body["top_k"] >= 1
    assert "embedding_model" in body
    assert isinstance(body["vectors_count"], int)


def test_status_requires_bearer_when_api_token_set(monkeypatch, client: TestClient) -> None:
    monkeypatch.setenv("API_TOKEN", "secret-token")
    from src.config import reset_settings

    reset_settings()
    assert client.get("/status").status_code == 401
    r = client.get(
        "/status",
        headers={"Authorization": "Bearer secret-token"},
    )
    assert r.status_code == 200


def test_ingest_files_requires_bearer_when_api_token_set(monkeypatch, client: TestClient) -> None:
    monkeypatch.setenv("API_TOKEN", "secret-token")
    from src.config import reset_settings

    reset_settings()
    response = client.post(
        "/ingest/files",
        files=[("files", ("a.txt", BytesIO(b"hello"), "text/plain"))],
    )
    assert response.status_code == 401
    auth = {"Authorization": "Bearer secret-token"}
    response = client.post(
        "/ingest/files",
        headers=auth,
        files=[("files", ("evil.exe", BytesIO(b"MZ\x90\x00"), "application/octet-stream"))],
    )
    assert response.status_code == 400
    assert "Unsupported" in response.json()["detail"]


def test_ingest_urls_validates_payload(client: TestClient) -> None:
    response = client.post("/ingest/urls", json={"urls": []})
    assert response.status_code == 422


def test_chat_returns_409_when_collection_empty_in_chroma_mode(
    monkeypatch, client: TestClient
) -> None:
    """In chroma mode with no ingested docs, /chat should fail loudly with 409."""
    monkeypatch.setenv("RETRIEVER_PROVIDER", "chroma")
    from src.config import reset_settings

    reset_settings()
    with patch("api.main.count_documents", return_value=0):
        response = client.post("/chat", json={"question": "hello", "history": []})
    assert response.status_code == 409
    assert "ingest" in response.json()["detail"].lower()


def test_chat_returns_409_in_keyword_mode_without_kb_dir(
    monkeypatch, client: TestClient
) -> None:
    """In keyword mode with no KB dir, /chat should fail with 409."""
    monkeypatch.setenv("RETRIEVER_PROVIDER", "keyword")
    from src.config import reset_settings

    reset_settings()
    with patch("api.main._KB_DIR") as mock_kb:
        mock_kb.exists.return_value = False
        response = client.post("/chat", json={"question": "hello", "history": []})
    assert response.status_code == 409


def test_chat_happy_path_with_mocked_llm(client: TestClient) -> None:
    """End-to-end /chat wiring: history, response shape, sources - no real LLM call."""

    class FakeBot:
        def ask(self, question, chat_history=None):
            assert question == "What is RAG?"
            assert len(chat_history) == 2
            return RAGResponse(answer="RAG = retrieve + generate.", sources=[])

    app.dependency_overrides[get_chatbot] = lambda: FakeBot()
    try:
        with patch("api.main.count_documents", return_value=5):
            response = client.post(
                "/chat",
                json={
                    "question": "What is RAG?",
                    "history": [
                        {"role": "user", "content": "hi"},
                        {"role": "assistant", "content": "hello!"},
                    ],
                },
            )
        assert response.status_code == 200
        body = response.json()
        assert body["answer"] == "RAG = retrieve + generate."
        assert body["sources"] == []
    finally:
        app.dependency_overrides.clear()


def test_chat_validates_empty_question(client: TestClient) -> None:
    response = client.post("/chat", json={"question": "", "history": []})
    assert response.status_code == 422
