"""Streamlit UI — ShopSmart BD RAG Chatbot  (v2).

Changes vs v1:
  • RETRIEVER_PROVIDER defaults to "chroma"  (semantic vector search).
  • AUTO_INGEST_ON_STARTUP defaults to "true" (indexes KB on cold start).
  • Dark sidebar, dot-grid canvas, gradient hero, modern card/chip UI.
  • Welcome state with suggested-question chips.
  • Honest stack-caption pill (shows actual retriever + vector count).
  • Admin telemetry gated behind password / collapsed expander.
"""

from __future__ import annotations

import os

# ── Force ChromaDB + auto-ingest as defaults (Streamlit secrets still override) ──
os.environ.setdefault("RETRIEVER_PROVIDER", "chroma")
os.environ.setdefault("AUTO_INGEST_ON_STARTUP", "true")

# Suppress noisy progress bars before heavy model imports.
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import logging
from pathlib import Path

import streamlit as st

# src/__init__.py shims pysqlite3 → sqlite3 before chromadb is imported.
from src.config import get_settings
from src.ingest import ingest_path, ingest_uploaded_file, ingest_urls
from src.keyword_retriever import clear_keyword_cache
from src.rag_chain import RAGChatbot, build_chat_history
from src.vector_store import count_documents, reset_collection

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger(__name__)

st.set_page_config(
    page_title="ShopSmart BD — AI Support",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR            = Path(__file__).parent / "data"
SHOPSMART_DOCS_DIR  = DATA_DIR / "shopsmart_docs"

SUGGESTED_QUESTIONS = [
    "🚚  How long does delivery take to Dhaka?",
    "↩️  What is your return & refund policy?",
    "💳  Do you accept bKash and Nagad?",
    "📦  How can I track my order?",
    "🛍️  What products do you carry?",
    "🌏  Do you ship outside Bangladesh?",
]


# ── Cache helpers ─────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="📚  Indexing ShopSmart knowledge base — first run may take 1–2 min…")
def _boot_knowledge_base() -> None:
    if count_documents() > 0:
        return
    ingest_path(SHOPSMART_DOCS_DIR)
    log.info("Auto-ingested ShopSmart docs into ChromaDB.")


@st.cache_resource(show_spinner="🤖  Warming up the RAG pipeline…")
def get_chatbot() -> RAGChatbot:
    return RAGChatbot()


def init_session_state() -> None:
    for key, default in {
        "messages": [],
        "ingested_sources": [],
        "admin_unlocked": False,
        "pending_prompt": None,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default


# ── Helpers ───────────────────────────────────────────────────────────────────

def _admin_unlocked(s) -> bool:
    return True if not s.admin_password else bool(st.session_state.get("admin_unlocked"))


def _llm_label(s) -> str:
    if s.llm_provider == "groq":   return f"Groq `{s.groq_model}`"
    if s.llm_provider == "openai": return f"OpenAI `{s.openai_model}`"
    return f"Ollama `{s.ollama_model}`"


def _stack_caption(s) -> str:
    retriever = "ChromaDB · semantic search" if s.retriever_provider == "chroma" else "Keyword search"
    return f"LangChain · {retriever} · {_llm_label(s)}"


def _status_pill(s) -> None:
    """Inline pill showing retriever status and vector count."""
    if s.retriever_provider == "chroma":
        n = count_documents()
        if n > 0:
            bg, fg, txt = "#D6F5E3", "#1A6640", f"● SEMANTIC SEARCH  ·  {n:,} vectors"
        else:
            bg, fg, txt = "#FFF5D6", "#8A6200", "◌  INDEXING KNOWLEDGE BASE…"
    else:
        bg, fg, txt = "#FFF5D6", "#8A6200", "● KEYWORD SEARCH"
    st.markdown(
        f'<span style="background:{bg};color:{fg};font-family:\'Source Sans 3\',sans-serif;'
        f'font-size:11px;font-weight:700;letter-spacing:.06em;padding:4px 12px;'
        f'border-radius:999px;display:inline-block;margin-bottom:16px;">{txt}</span>',
        unsafe_allow_html=True,
    )


# ── Brand CSS ─────────────────────────────────────────────────────────────────

_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap');

:root{
  --red:#E63946; --red-d:#C5313D; --red-l:rgba(230,57,70,.12);
  --org:#E8734A; --yel:#F5A623;
  --cv:#FAF7F2;  --wh:#FFFFFF;
  --s50:#F5EFE6; --s100:#EDE3D4; --s200:#D6C9B5;
  --s300:#B8A894;--s400:#8A7A6A;--s500:#5C4E42;--s900:#1A1210;
  --sb-bg:#1A1210; --sb-bg2:#221712;
  --fd:'Manrope',system-ui,sans-serif;
  --fb:'Source Sans 3',system-ui,sans-serif;
}

/* ── Canvas: warm paper + dot grid ── */
.stApp{
  background-color:var(--cv) !important;
  background-image:radial-gradient(var(--s200) 1px,transparent 1px) !important;
  background-size:28px 28px !important;
}
[data-testid="stHeader"]{
  background:var(--cv) !important;
  border-bottom:1px solid var(--s100) !important;
}
[data-testid="stAppViewBlockContainer"]{padding-top:1.5rem !important;}

/* ── Sidebar: rich dark ── */
section[data-testid="stSidebar"]>div:first-child{
  background:linear-gradient(170deg,var(--sb-bg) 0%,var(--sb-bg2) 100%) !important;
  border-right:1px solid rgba(230,57,70,.18) !important;
}
section[data-testid="stSidebar"] h1{
  color:#FFF !important; font-family:var(--fd) !important;
  font-weight:800 !important; font-size:18px !important;
  letter-spacing:-.01em !important;
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{
  color:#E0D0BC !important; font-family:var(--fd) !important;
  font-weight:800 !important; font-size:10px !important;
  text-transform:uppercase !important; letter-spacing:.12em !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li{
  color:#A89880 !important; font-family:var(--fb) !important; font-size:13px !important;
}
section[data-testid="stSidebar"] [data-testid="stText"],
section[data-testid="stSidebar"] .stText{color:#786858 !important; font-family:var(--fb) !important;}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] .stCaption{color:#5A4A3C !important;}
section[data-testid="stSidebar"] hr,[data-testid="stDivider"] hr{
  border-color:rgba(255,255,255,.07) !important;
}
section[data-testid="stSidebar"] .stButton>button{
  background:rgba(255,255,255,.06) !important;
  border:1px solid rgba(255,255,255,.1) !important;
  color:#D8C8B4 !important; font-family:var(--fb) !important;
  font-weight:600 !important; border-radius:8px !important;
  transition:all 140ms !important; text-align:left !important;
}
section[data-testid="stSidebar"] .stButton>button:hover{
  background:rgba(230,57,70,.18) !important;
  border-color:rgba(230,57,70,.35) !important;
  color:#FFF !important;
}
section[data-testid="stSidebar"] [data-testid="stAlert"]{
  background:rgba(255,255,255,.05) !important;
  border:1px solid rgba(255,255,255,.08) !important; border-radius:8px !important;
}
section[data-testid="stSidebar"] [data-testid="stAlert"] p{color:#A89880 !important;}
section[data-testid="stSidebar"] [data-testid="stExpander"]{
  background:rgba(255,255,255,.04) !important;
  border:1px solid rgba(255,255,255,.09) !important; border-radius:8px !important;
}
section[data-testid="stSidebar"] [data-testid="stExpander"] summary,
section[data-testid="stSidebar"] [data-testid="stExpander"] p{color:#C0B0A0 !important;}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea{
  background:rgba(255,255,255,.07) !important;
  border:1px solid rgba(255,255,255,.13) !important;
  color:#E8DDD0 !important; border-radius:6px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]{
  background:rgba(255,255,255,.04) !important;
  border:1.5px dashed rgba(255,255,255,.14) !important; border-radius:8px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] p{color:#786858 !important;}

/* ── Main typography ── */
[data-testid="stMarkdownContainer"] h1,
[data-testid="stHeadingWithActionElements"] h1{
  font-family:var(--fd) !important; font-weight:800 !important;
  font-size:28px !important; color:var(--s900) !important; letter-spacing:-.02em !important;
}
[data-testid="stMarkdownContainer"] h2,
[data-testid="stHeadingWithActionElements"] h2{
  font-family:var(--fd) !important; font-weight:800 !important;
  color:var(--s900) !important; letter-spacing:-.01em !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li{font-family:var(--fb) !important; color:var(--s500) !important;}
[data-testid="stCaptionContainer"],.stCaption{font-family:var(--fb) !important; color:var(--s400) !important;}

/* ── Buttons ── */
.stButton>button{
  font-family:var(--fb) !important; font-weight:600 !important;
  border-radius:8px !important; transition:all 120ms ease !important;
  white-space:normal !important; line-height:1.35 !important; text-align:left !important;
}
.stButton>button[data-testid="baseButton-primary"]{
  background:var(--red) !important; border-color:var(--red) !important;
  color:#fff !important; box-shadow:0 2px 10px rgba(230,57,70,.28) !important;
}
.stButton>button[data-testid="baseButton-primary"]:hover{
  background:var(--red-d) !important; border-color:var(--red-d) !important;
  transform:translateY(-1px) !important; box-shadow:0 4px 16px rgba(230,57,70,.38) !important;
}
.stButton>button[data-testid="baseButton-secondary"]{
  background:var(--wh) !important; border:1px solid var(--s100) !important;
  color:var(--s900) !important; box-shadow:0 1px 4px rgba(0,0,0,.05) !important;
}
.stButton>button[data-testid="baseButton-secondary"]:hover{
  background:var(--s50) !important; border-color:var(--s200) !important;
  transform:translateY(-1px) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"]{
  background:var(--wh) !important;
  border:1.5px solid var(--s100) !important;
  border-radius:12px !important;
  box-shadow:0 2px 16px rgba(0,0,0,.07) !important;
}
[data-testid="stChatInput"]:focus-within{
  border-color:var(--red) !important;
  box-shadow:0 0 0 3px rgba(230,57,70,.1),0 2px 16px rgba(0,0,0,.07) !important;
}
[data-testid="stChatInput"] textarea{
  font-family:var(--fb) !important; font-size:15px !important; color:var(--s900) !important;
}
[data-testid="stChatInput"] textarea::placeholder{color:var(--s300) !important;}

/* ── Chat bubbles ── */
[data-testid="stChatMessage"]{
  border-radius:12px !important; padding:14px 16px !important;
  margin:4px 0 !important; transition:box-shadow 120ms !important;
}
[data-testid="stChatMessage"]:has([data-testid*="chatAvatarIcon-user"]){
  background:linear-gradient(135deg,rgba(230,57,70,.07) 0%,rgba(232,115,74,.04) 100%) !important;
  border:1px solid rgba(230,57,70,.13) !important;
}
[data-testid="stChatMessage"]:has([data-testid*="chatAvatarIcon-assistant"]){
  background:var(--wh) !important;
  border:1px solid var(--s100) !important;
  box-shadow:0 1px 8px rgba(0,0,0,.04) !important;
}
[data-testid="stChatMessageContent"] p{
  font-family:var(--fb) !important; font-size:15px !important;
  line-height:1.6 !important; color:var(--s900) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"]{
  border:1px solid var(--s100) !important; border-radius:10px !important;
  overflow:hidden !important; box-shadow:0 1px 4px rgba(0,0,0,.03) !important;
}

/* ── Alerts ── */
[data-testid="stAlert"]{border-radius:10px !important;}
[data-testid="stAlert"] p{font-family:var(--fb) !important;}

/* ── Textarea ── */
.stTextArea textarea{
  font-family:var(--fb) !important; background:var(--wh) !important;
  border:1px solid var(--s100) !important; border-radius:8px !important; color:var(--s900) !important;
}
.stTextArea textarea:focus{
  border-color:var(--red) !important; box-shadow:0 0 0 2px rgba(230,57,70,.1) !important;
}
</style>"""


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar() -> None:
    s = get_settings()
    with st.sidebar:
        # gradient accent bar
        st.markdown(
            '<div style="height:3px;background:linear-gradient(90deg,#E63946,#E8734A,#F5A623);'
            'border-radius:2px;margin-bottom:20px;"></div>',
            unsafe_allow_html=True,
        )
        st.title("🛍️  ShopSmart BD")
        st.caption("AI-powered customer support")

        st.divider()
        st.subheader("Chat")
        turns = len(st.session_state.messages) // 2
        st.markdown(
            f'<div style="font-family:\'Source Sans 3\',sans-serif;font-size:13px;'
            f'color:#786858;margin-bottom:10px;">Turns: <strong style="color:#D8C8B4;">'
            f'{turns}</strong></div>',
            unsafe_allow_html=True,
        )
        if st.button("✕  Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.subheader("Help topics")
        st.markdown(
            "- 📦  Delivery & tracking\n"
            "- ↩️  Returns & refunds\n"
            "- 💳  bKash, Nagad & cards\n"
            "- 🛡️  Warranty & support\n"
            "- 🛍️  Products & categories",
        )

        # ── Admin gate ────────────────────────────────────────────────────────
        if s.admin_password and not _admin_unlocked(s):
            st.divider()
            with st.expander("🔒  Staff login", expanded=False):
                with st.form("admin_login"):
                    pwd = st.text_input("Password", type="password", label_visibility="collapsed",
                                        placeholder="Admin password")
                    if st.form_submit_button("Unlock admin tools", use_container_width=True):
                        if pwd == s.admin_password:
                            st.session_state.admin_unlocked = True
                            st.success("Admin tools unlocked.")
                            st.rerun()
                        else:
                            st.error("Incorrect password.")
            return

        if not _admin_unlocked(s):
            return

        if s.admin_password:
            st.divider()
            if st.button("🔓  Lock admin tools", use_container_width=True):
                st.session_state.admin_unlocked = False
                st.rerun()

        st.divider()
        with st.expander("⚙️  System status", expanded=False):
            n = count_documents() if s.retriever_provider == "chroma" else "n/a"
            st.markdown(
                f"- **LLM:** {_llm_label(s)}\n"
                f"- **Retriever:** `{s.retriever_provider}`\n"
                f"- **Embeddings:** `{s.embedding_model.split('/')[-1]}`\n"
                f"- **Chunk size:** `{s.chunk_size}` / overlap `{s.chunk_overlap}`\n"
                f"- **Top-K:** `{s.top_k}`\n"
                f"- **Vectors:** `{n}`"
            )

        if not s.enable_public_admin:
            st.info("Document management disabled. Use the CLI to load the KB.")
            return

        st.divider()
        st.subheader("Knowledge Base")
        if s.retriever_provider == "keyword":
            st.success("Ready  (keyword mode)")
            if st.button("↺  Reload KB", use_container_width=True):
                clear_keyword_cache(); get_chatbot.clear()
                st.success("Cache cleared.")
        elif st.button("⬆  Load ShopSmart KB", use_container_width=True):
            with st.spinner("Indexing…"):
                try:
                    ingest_path(SHOPSMART_DOCS_DIR)
                    st.session_state.ingested_sources += ["faq.txt","policies.txt","products.txt"]
                    get_chatbot.clear()
                    st.success("3 documents indexed ✓")
                except Exception as e:
                    st.error(f"Failed: {e}")

        st.divider()
        st.subheader("Add documents")
        uploaded = st.file_uploader(
            "PDF / TXT / MD / DOCX", type=["pdf","txt","md","docx"],
            accept_multiple_files=True, label_visibility="collapsed",
        )
        if uploaded and st.button("⬆  Ingest files", use_container_width=True):
            total = 0
            dest = SHOPSMART_DOCS_DIR if s.retriever_provider == "keyword" else DATA_DIR
            for f in uploaded:
                with st.spinner(f"Ingesting {f.name}…"):
                    try:
                        total += ingest_uploaded_file(f.name, f.getvalue(), dest)
                        st.session_state.ingested_sources.append(f.name)
                    except Exception as e:
                        st.error(f"{f.name}: {e}")
            if total:
                st.success(f"{total} chunks from {len(uploaded)} file(s) ✓")
                if s.retriever_provider == "keyword": clear_keyword_cache()
                get_chatbot.clear()

        url_input = st.text_area("Paste URLs (one per line)",
                                  placeholder="https://example.com/…", height=80)
        if st.button("⬆  Ingest URLs", use_container_width=True):
            urls = [u.strip() for u in url_input.splitlines() if u.strip()]
            if not urls:
                st.warning("No URLs entered.")
            else:
                with st.spinner(f"Fetching {len(urls)} URL(s)…"):
                    try:
                        n = ingest_urls(urls)
                        st.success(f"{n} chunks from {len(urls)} URL(s) ✓")
                        st.session_state.ingested_sources += urls
                        get_chatbot.clear()
                    except Exception as e:
                        st.error(f"Failed: {e}")

        st.divider()
        if st.button("🗑  Reset vector DB", use_container_width=True, type="secondary"):
            reset_collection(); st.session_state.ingested_sources = []
            get_chatbot.clear(); _boot_knowledge_base.clear()
            st.success("Vector store cleared.")
            st.rerun()

        if st.session_state.ingested_sources:
            with st.expander("Ingested this session", expanded=False):
                for src in st.session_state.ingested_sources:
                    st.write(f"- {src}")


# ── Empty state ───────────────────────────────────────────────────────────────

def render_empty_state() -> None:
    st.markdown("""
<div style="background:#fff;border-radius:16px;overflow:hidden;
  box-shadow:0 4px 24px rgba(26,18,16,.08),0 1px 4px rgba(0,0,0,.04);
  margin-bottom:24px;">
  <div style="height:4px;background:linear-gradient(90deg,#E63946,#E8734A,#F5A623);"></div>
  <div style="padding:28px 32px 32px;">
    <div style="width:52px;height:52px;border-radius:14px;
      background:linear-gradient(135deg,#E63946,#E8734A);
      display:flex;align-items:center;justify-content:center;
      font-size:26px;margin-bottom:16px;
      box-shadow:0 4px 14px rgba(230,57,70,.30);">🛍️</div>
    <div style="font-family:'Source Sans 3',sans-serif;font-weight:700;font-size:10px;
      letter-spacing:.16em;color:#E63946;text-transform:uppercase;margin-bottom:8px;">
      ShopSmart Support</div>
    <div style="font-family:'Manrope',sans-serif;font-weight:800;font-size:26px;
      line-height:1.15;letter-spacing:-.02em;color:#1A1210;margin-bottom:10px;">
      Hi, I'm Shira 👋<br>How can I help today?</div>
    <div style="font-family:'Source Sans 3',sans-serif;font-size:15px;
      line-height:1.6;color:#5C4E42;max-width:52ch;">
      Ask about orders, delivery, returns, payments, warranties, or products.
      I cite the source document with every answer so you know where it came from.
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(
        '<div style="font-family:\'Source Sans 3\',sans-serif;font-weight:700;font-size:11px;'
        'color:#8A7A6A;text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px;">'
        '✦  Try asking</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        if cols[i % 2].button(q, key=f"sq_{i}", use_container_width=True):
            st.session_state.pending_prompt = q
            st.rerun()


# ── Sources ───────────────────────────────────────────────────────────────────

def render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander("📄  View sources", expanded=False):
        for i, src in enumerate(sources, 1):
            name = (src.get("filename") or src.get("title")
                    or Path(src.get("source","unknown")).name)
            st.markdown(f"**{i}. {name}**")
            st.caption(src.get("snippet","")[:140].strip())


# ── Chat ──────────────────────────────────────────────────────────────────────

def render_chat() -> None:
    s = get_settings()

    # ── Header ──
    st.markdown("## ShopSmart BD — Customer Support")
    st.caption(_stack_caption(s))
    _status_pill(s)
    st.divider()

    # ── Welcome or conversation ──
    if not st.session_state.messages:
        render_empty_state()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            render_sources(msg.get("sources", []))

    # ── Input (chip click takes priority over text box) ──
    pending = st.session_state.pop("pending_prompt", None)
    prompt  = pending or st.chat_input("Ask about your order, returns, payments…")
    if not prompt:
        return

    docs_ok = (
        s.retriever_provider == "keyword" and SHOPSMART_DOCS_DIR.exists()
    ) or count_documents() > 0
    if not docs_ok:
        st.warning("Knowledge base is still loading — please wait a moment and try again.")
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base…"):
            try:
                pairs = []
                msgs  = st.session_state.messages[:-1]
                for i in range(0, len(msgs) - 1, 2):
                    if msgs[i]["role"] == "user" and msgs[i+1]["role"] == "assistant":
                        pairs.append((msgs[i]["content"], msgs[i+1]["content"]))
                resp = get_chatbot().ask(prompt, chat_history=build_chat_history(pairs))
            except Exception as exc:
                st.error(f"Error: {exc}")
                return
            st.markdown(resp.answer)
            sources = resp.formatted_sources()
            render_sources(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": resp.answer, "sources": sources}
    )
    if pending:
        st.rerun()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    init_session_state()
    s = get_settings()
    boot_error = ""

    if s.auto_ingest_on_startup:
        try:
            _boot_knowledge_base()
        except Exception as exc:
            log.warning("Auto-ingest failed: %s", exc)
            boot_error = str(exc)

    render_sidebar()

    if boot_error:
        st.error(
            f"⚠️  Could not auto-load the knowledge base: {boot_error}\n\n"
            "Use **⬆ Load ShopSmart KB** in the admin panel to retry, or switch "
            "`RETRIEVER_PROVIDER=keyword` in Streamlit secrets for zero-dependency mode."
        )

    render_chat()


if __name__ == "__main__":
    main()
