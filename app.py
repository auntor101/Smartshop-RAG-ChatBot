"""Streamlit UI for the LLM-Powered RAG Chatbot."""

from __future__ import annotations

import os

# Windows + Streamlit: tqdm (used by transformers) flushing stderr can raise
# OSError: [Errno 22] Invalid argument. Disable hub/tqdm bars before Streamlit.
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
# Avoid tokenizer fork warnings; slightly reduces overhead on Windows.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import logging
from pathlib import Path

import streamlit as st

# src/__init__.py patches sqlite3 → pysqlite3 before chromadb is imported.
# These imports must come after that __init__ runs.
from src.config import get_settings
from src.ingest import ingest_path, ingest_uploaded_file, ingest_urls
from src.rag_chain import RAGChatbot, build_chat_history
from src.vector_store import count_documents, reset_collection

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

st.set_page_config(
    page_title="ShopSmart BD Support",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"
SHOPSMART_DOCS_DIR = DATA_DIR / "shopsmart_docs"


@st.cache_resource(show_spinner="Loading ShopSmart knowledge base...")
def _boot_knowledge_base() -> None:
    """Ingest the bundled KB on first cold start when the vector store is empty.

    Cached for the process lifetime on success. If ``ingest_path`` raises, the
    exception is not cached (Streamlit skips the cache entry), so a later rerun
    or manual retry can succeed without restarting the server.
    """
    if count_documents() > 0:
        return
    ingest_path(SHOPSMART_DOCS_DIR)
    logging.getLogger(__name__).info("Auto-ingested ShopSmart knowledge base.")


@st.cache_resource(show_spinner="Initialising RAG pipeline...")
def get_chatbot() -> RAGChatbot:
    return RAGChatbot()


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "ingested_sources" not in st.session_state:
        st.session_state.ingested_sources = []
    if "admin_unlocked" not in st.session_state:
        st.session_state.admin_unlocked = False


def _admin_unlocked(settings) -> bool:
    if not settings.admin_password:
        return True
    return bool(st.session_state.get("admin_unlocked"))


def _llm_caption(settings) -> str:
    if settings.llm_provider == "groq":
        return f"Groq `{settings.groq_model}`"
    if settings.llm_provider == "openai":
        return f"OpenAI `{settings.openai_model}`"
    return f"Ollama `{settings.ollama_model}`"


def render_sidebar() -> None:
    settings = get_settings()
    with st.sidebar:
        st.title("ShopSmart BD")
        st.caption("Customer support knowledge base.")

        st.divider()
        st.subheader("Configuration")
        st.markdown(
            f"- **LLM provider:** `{settings.llm_provider}`\n"
            f"- **LLM model:** {_llm_caption(settings)}\n"
            f"- **Embeddings:** `{settings.embedding_model.split('/')[-1]}`\n"
            f"- **Chunk size:** `{settings.chunk_size}` (overlap `{settings.chunk_overlap}`)\n"
            f"- **Top-K:** `{settings.top_k}`\n"
            f"- **Vectors stored:** `{count_documents()}`"
        )

        st.divider()
        st.subheader("Chat")
        st.write(f"Turns: {len(st.session_state.messages) // 2}")
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        if not settings.enable_public_admin:
            st.divider()
            st.info(
                "Document management is disabled (`ENABLE_PUBLIC_ADMIN=false`). "
                "Use the operator or CLI to load the knowledge base."
            )
            return

        if settings.admin_password and not _admin_unlocked(settings):
            st.divider()
            st.subheader("Admin")
            with st.form("admin_login"):
                pwd = st.text_input("Admin password", type="password")
                submitted = st.form_submit_button("Unlock admin tools", use_container_width=True)
            if submitted:
                if pwd == settings.admin_password:
                    st.session_state.admin_unlocked = True
                    st.success("Admin tools unlocked for this session.")
                    st.rerun()
                else:
                    st.error("Incorrect password.")
            return

        if settings.admin_password and _admin_unlocked(settings):
            st.divider()
            if st.button("Lock admin tools", use_container_width=True):
                st.session_state.admin_unlocked = False
                st.rerun()

        st.divider()
        st.subheader("ShopSmart KB")
        if st.button("Load ShopSmart Knowledge Base", use_container_width=True):
            with st.spinner("Indexing ShopSmart knowledge base..."):
                try:
                    ingest_path(SHOPSMART_DOCS_DIR)
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Failed to load ShopSmart KB: {exc}")
                else:
                    st.session_state.ingested_sources.extend(
                        ["faq.txt", "policies.txt", "products.txt"]
                    )
                    get_chatbot.clear()
                    st.success("ShopSmart KB loaded — 3 documents indexed")

        st.divider()
        st.subheader("Add documents")
        uploaded = st.file_uploader(
            "Upload PDF / TXT / MD / DOCX",
            type=["pdf", "txt", "md", "docx"],
            accept_multiple_files=True,
        )
        if uploaded and st.button("Ingest uploaded files", use_container_width=True):
            total_chunks = 0
            for f in uploaded:
                with st.spinner(f"Ingesting {f.name}..."):
                    try:
                        added = ingest_uploaded_file(f.name, f.getvalue(), DATA_DIR)
                        total_chunks += added
                        st.session_state.ingested_sources.append(f.name)
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Failed to ingest {f.name}: {exc}")
            if total_chunks:
                st.success(f"Added {total_chunks} chunks across {len(uploaded)} file(s).")
                get_chatbot.clear()

        url_input = st.text_area(
            "Or paste URLs (one per line)",
            placeholder="https://example.com/article",
            height=100,
        )
        if st.button("Ingest URLs", use_container_width=True):
            urls = [u.strip() for u in url_input.splitlines() if u.strip()]
            if not urls:
                st.warning("Please paste at least one URL.")
            else:
                with st.spinner(f"Fetching {len(urls)} URL(s)..."):
                    try:
                        added = ingest_urls(urls)
                        st.success(f"Added {added} chunks from {len(urls)} URL(s).")
                        st.session_state.ingested_sources.extend(urls)
                        get_chatbot.clear()
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Failed to ingest URLs: {exc}")

        st.divider()
        st.subheader("Session")
        if st.button("Reset DB", use_container_width=True, type="secondary"):
            reset_collection()
            st.session_state.ingested_sources = []
            get_chatbot.clear()
            _boot_knowledge_base.clear()
            st.success("Vector store cleared.")
            st.rerun()

        if st.session_state.ingested_sources:
            with st.expander("Ingested in this session", expanded=False):
                for s in st.session_state.ingested_sources:
                    st.write(f"- {s}")


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return

    with st.expander("View sources", expanded=False):
        for i, src in enumerate(sources, start=1):
            filename = src.get("filename") or src.get("title") or Path(
                src.get("source", "unknown")
            ).name
            snippet = src.get("snippet", "")[:120].strip()
            st.markdown(f"**{i}. {filename}**")
            st.caption(snippet)


def render_chat() -> None:
    settings = get_settings()
    st.markdown("## ShopSmart BD — Customer Support")
    st.caption(
        f"Powered by LangChain + ChromaDB + {_llm_caption(settings)} | "
        "Ask about your order or our products."
    )
    st.divider()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            render_sources(msg.get("sources", []))

    prompt = st.chat_input("Ask a question about your documents...")
    if not prompt:
        return

    if count_documents() == 0:
        st.warning("No documents have been ingested yet. Use the sidebar to add some.")
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                history_pairs = []
                msgs = st.session_state.messages[:-1]
                for i in range(0, len(msgs) - 1, 2):
                    if msgs[i]["role"] == "user" and msgs[i + 1]["role"] == "assistant":
                        history_pairs.append((msgs[i]["content"], msgs[i + 1]["content"]))

                response = get_chatbot().ask(
                    prompt, chat_history=build_chat_history(history_pairs)
                )
            except Exception as exc:  # noqa: BLE001
                st.error(f"Error: {exc}")
                return

            st.markdown(response.answer)
            sources = response.formatted_sources()
            render_sources(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": response.answer, "sources": sources}
    )


def main() -> None:
    init_session_state()
    boot_error = ""
    try:
        # First cold start downloads the embedding model; show feedback without
        # blocking the rest of the app on subsequent runs (count uses Chroma only).
        if count_documents() == 0 and SHOPSMART_DOCS_DIR.exists():
            with st.spinner(
                "Preparing the knowledge base — first launch can take 1–2 minutes "
                "while the embedding model loads…"
            ):
                _boot_knowledge_base()
        else:
            _boot_knowledge_base()
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Auto-ingest failed: %s", exc)
        boot_error = str(exc)
    render_sidebar()
    if boot_error:
        st.error(
            f"Could not auto-load the ShopSmart knowledge base: {boot_error}\n\n"
            "Use **Load ShopSmart Knowledge Base** in the sidebar to retry, or check "
            "that `data/shopsmart_docs` exists and ChromaDB can write to `CHROMA_PERSIST_DIR`."
        )
    render_chat()


if __name__ == "__main__":
    main()
