# ShopSmart BD — Shira Chatbot (Streamlit)

A Streamlit-native chat interface for **Shira**, ShopSmart BD's customer support assistant.
Styled with the full ShopSmart BD design system — warm paper background, Manrope display,
Source Sans 3 body, brand-red accents.

---

## Folder structure

```
streamlit/
├── streamlit_app.py          ← entry point
├── responses.py              ← intent matching (swap for real RAG here)
├── requirements.txt
├── .streamlit/
│   └── config.toml           ← brand theme tokens
└── assets/
    ├── shira-avatar.svg
    ├── mark.svg
    ├── logo.svg
    ├── payments/             ← bKash, Nagad, Visa, MC, PayPal, COD
    ├── illustrations/        ← delivery.svg, empty-cart.svg
    └── photos/               ← placeholder.svg
```

---

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Opens at **http://localhost:8501**

---

## Deploy to Streamlit Cloud

1. Push this folder (or the whole repo) to a **GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Choose the repo, branch, and set **Main file path** to:
   ```
   streamlit/streamlit_app.py
   ```
   (or just `streamlit_app.py` if you deploy the `streamlit/` folder as the repo root)
4. Click **Deploy** — that's it.

Streamlit Cloud reads `requirements.txt` automatically and serves the app.

---

## Plugging in a real LLM / RAG backend

All response logic lives in **`responses.py`** → `find_reply(text: str) -> dict`.

The return shape the UI expects:

```python
{
    "kind":     "text" | "product" | "payments" | "delivery",
    "text":     str,                      # always required
    "sources":  list[str],                # shown in expandable citation panel
    "products": list[dict] | None,        # only for kind="product"
}
```

A product dict:

```python
{
    "name":      str,
    "price":     int,          # BDT, no decimals
    "blurb":     str,
    "stock":     "in" | "low" | "out",
    "stockNote": str | None,   # e.g. "3 left"
    "warranty":  str,
}
```

### LangChain / RAG example

```python
from langchain_core.runnables import RunnableLambda

chain = your_rag_chain  # returns {"answer": str, "source_documents": [...]}

def find_reply(text: str) -> dict:
    result = chain.invoke({"question": text})
    sources = [doc.metadata.get("source", "") for doc in result["source_documents"]]
    return {
        "kind":    "text",
        "text":    result["answer"],
        "sources": sources,
    }
```

---

## Customisation quick-ref

| What to change | Where |
|---|---|
| Brand colours | `.streamlit/config.toml` + `:root` block in `_inject_css()` |
| Suggestion chips | `SUGGESTIONS` list in `responses.py` |
| Product catalogue | `PRODUCTS` list in `responses.py` |
| Response logic | `find_reply()` in `responses.py` |
| Avatar / assets | `assets/` folder |
| Page title / icon | `st.set_page_config()` in `streamlit_app.py` |

---

## Requirements

- Python ≥ 3.10
- Streamlit ≥ 1.35.0
