# ShopSmart BD — AI Customer Support Chatbot

ShopSmart BD is a domain-specific AI customer support chatbot for a fictional Bangladeshi e-commerce store. It uses the existing LangChain RAG pipeline, ChromaDB persistence, local sentence-transformer embeddings, and pluggable Groq/OpenAI/Ollama LLM providers to answer customer questions about shipping, returns, payments, accounts, discounts, warranties, and products with grounded source citations.

## Run locally (Windows)

1. Clone or open this repo, then from the repo root:
   - **Chat UI:** double-click `run.bat`, or run `.\scripts\run.ps1` in PowerShell.
   - **REST API:** double-click `run-api.bat`, or run `.\scripts\run_api.ps1` (then open http://127.0.0.1:8000/docs).

2. The first run creates `.env` from `.env.example` if it is missing. Edit `.env` and set a real **`GROQ_API_KEY`** (default `LLM_PROVIDER=groq`), or switch to OpenAI/Ollama per `.env.example`.

3. Open **http://localhost:8501** for the chatbot. Use **Load ShopSmart Knowledge Base** in the sidebar to index the bundled docs, or set `AUTO_INGEST_ON_STARTUP=true` in `.env` if you want this to happen before first render.

Manual equivalent:

```powershell
pip install -r requirements.txt
copy .env.example .env   # if you do not have .env yet
cmd /c "echo.| python -m streamlit run app.py"
```

## Architecture

```text
User Query
   ↓
History-Aware Question Rewriter (LangChain)
   ↓
ChromaDB Retriever (top-k semantic search)
   ↓
Local embeddings (all-MiniLM-L6-v2)
   ↓
LLM (GPT-4o-mini / Groq Llama-3)
   ↓
Grounded Answer + Source Citations
```

## Tech Stack

| Framework | Tool | Purpose |
| --- | --- | --- |
| App UI | Streamlit | Customer support chat interface and source display |
| API | FastAPI | REST backend for programmatic chat and ingestion |
| Orchestration | LangChain | History-aware retrieval and answer generation chain |
| Vector Database | ChromaDB | Persistent semantic document store |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Fast local embeddings with no API cost |
| LLM Providers | Groq, OpenAI, Ollama | Configurable answer generation |
| Document Loading | LangChain Community loaders | Load TXT, Markdown, PDF, DOCX, and URLs |

## Setup

```bash
git clone https://github.com/dleelaprasad24/LLM-RAG-Chatbot.git
cd LLM-RAG-Chatbot
pip install -r requirements.txt
cp .env.example .env
```

Set your API keys in `.env`. For the default setup, set `LLM_PROVIDER=groq` and provide `GROQ_API_KEY`.

### Security (public hosting)

If you expose Streamlit or the API on the internet, set at least:

| Variable | Purpose |
| --- | --- |
| `ADMIN_PASSWORD` | Locks sidebar actions: load KB, file upload, URL ingest, reset DB. |
| `ENABLE_PUBLIC_ADMIN` | Set to `false` for a chat-only UI with no ingest controls. |
| `API_TOKEN` | If you run FastAPI, protects `/status`, `/ingest/*`, and `DELETE /collection` with `Authorization: Bearer <token>`. |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins for the API; leave empty for `*` (local dev only). |
| `URL_ALLOWLIST` | Optional comma-separated hostnames allowed for URL ingestion (extra lockdown). |

Local development works with these unset (open admin, open API meta routes).

Start the Streamlit app:

```bash
streamlit run app.py
```

Open `http://localhost:8501`. Use **Load ShopSmart Knowledge Base** in the sidebar to index the bundled docs. Then ask questions such as "What is your return policy?"

### Streamlit Community Cloud

Use these app settings:

- Repository: `auntor101/Smartshop-RAG-ChatBot`
- Branch: `main`
- Main file path: `app.py`

Add `GROQ_API_KEY` in **App settings → Secrets**. Keep `AUTO_INGEST_ON_STARTUP=false` on Community Cloud so the page renders before heavy embedding work starts.

### REST API (local)

```bash
uvicorn api.main:app --reload --port 8000
```

When `API_TOKEN` is set, send `Authorization: Bearer <API_TOKEN>` for `/status`, `POST /ingest/files`, `POST /ingest/urls`, and `DELETE /collection`. `/health` and `POST /chat` stay unauthenticated by default.

## License

MIT
