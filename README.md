# ShopSmart BD — AI Customer Support Chatbot

ShopSmart BD is a domain-specific AI customer support chatbot for a fictional Bangladeshi e-commerce store. It uses the existing LangChain RAG pipeline, ChromaDB persistence, HuggingFace sentence-transformer embeddings, and pluggable Groq/OpenAI/Ollama LLM providers to answer customer questions about shipping, returns, payments, accounts, discounts, warranties, and products with grounded source citations.

## Architecture

```text
User Query
   ↓
History-Aware Question Rewriter (LangChain)
   ↓
ChromaDB Retriever (top-k semantic search)
   ↓
HuggingFace Embeddings (all-MiniLM-L6-v2)
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
| Embeddings | HuggingFace all-MiniLM-L6-v2 | Fast local embeddings with no API cost |
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

Start the Streamlit app:

```bash
streamlit run app.py
```

Open `http://localhost:8501`, click **Load ShopSmart Knowledge Base**, and ask questions such as "What is your return policy?"

## HuggingFace Spaces Deployment

Create a new HuggingFace Space using the Streamlit SDK. Push this repository to the Space, then add required secrets such as `GROQ_API_KEY`, `OPENAI_API_KEY`, and `HUGGINGFACEHUB_API_TOKEN` in the Space settings. The Space will run `streamlit run app.py` and expose the ShopSmart BD chatbot UI.

## License

MIT
