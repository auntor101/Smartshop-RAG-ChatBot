"""
responses.py — RAG-backed reply handler for the Shira Streamlit UI.

SUGGESTIONS and PRODUCTS drive the welcome screen and product cards.
find_reply() delegates to the full LangChain RAG pipeline in src/.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# ── Windows / HuggingFace compat (before any heavy imports) ──────────────────
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# ── Ensure project root is on sys.path so src.* imports resolve ───────────────
# When Streamlit runs streamlit/streamlit_app.py it adds the streamlit/ dir to
# sys.path, but not the project root where src/ lives.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.rag_chain import RAGChatbot, build_chat_history

# ── Product catalogue (drives product-card rich UI) ───────────────────────────
PRODUCTS: list[dict] = [
    {
        "name": "SmartX Nova 5G Phone",
        "price": 24990,
        "category": "Electronics",
        "stock": "in",
        "warranty": "6 months",
        "blurb": "Lightweight Android with bright AMOLED display, 128 GB, all-day battery.",
    },
    {
        "name": "BeatPro Wireless Earbuds",
        "price": 3490,
        "category": "Electronics",
        "stock": "low",
        "stockNote": "3 left",
        "warranty": "6 months",
        "blurb": "Touch controls, sweat-resistant, up to 24 hours with charging case.",
    },
    {
        "name": "VoltMate 20000mAh Power Bank",
        "price": 2190,
        "category": "Electronics",
        "stock": "in",
        "warranty": "6 months",
        "blurb": "Dual USB output, fast charging, slim travel body.",
    },
    {
        "name": "HomeView HD Security Camera",
        "price": 4590,
        "category": "Electronics",
        "stock": "out",
        "warranty": "6 months",
        "blurb": "Indoor Wi-Fi, 1080p, night vision, two-way audio.",
    },
    {
        "name": "Cotton Comfort Panjabi",
        "price": 1450,
        "category": "Fashion",
        "stock": "in",
        "warranty": "—",
        "blurb": "Breathable cotton panjabi for festivals and office events.",
    },
    {
        "name": "UrbanWalk Sneakers",
        "price": 2290,
        "category": "Fashion",
        "stock": "in",
        "warranty": "—",
        "blurb": "Cushioned soles, knitted upper, built for daily walking.",
    },
    {
        "name": "AromaBrew Electric Kettle",
        "price": 1790,
        "category": "Home & Kitchen",
        "stock": "low",
        "stockNote": "1 left",
        "warranty": "6 months",
        "blurb": "Stainless steel, auto shut-off, boil-dry protection.",
    },
]

# ── Welcome screen suggestion chips ──────────────────────────────────────────
SUGGESTIONS: list[str] = [
    "How long does delivery take?",
    "Can I pay with bKash?",
    "What is your return policy?",
    "Show me phones under BDT 25,000",
    "How does the referral program work?",
]

# ── Rich-card intent patterns ─────────────────────────────────────────────────
# These patterns select which visual card to show *alongside* the RAG answer.
# The RAG pipeline always provides the actual text; these add delivery/payment/
# product card chrome when the topic matches.
_RICH_INTENTS: list[dict] = [
    {
        "match": re.compile(r"deliver|shipping|how long|how soon|express|standard", re.I),
        "kind": "delivery",
    },
    {
        "match": re.compile(r"bkash|nagad|pay|payment|cod|cash.on.delivery|visa|card", re.I),
        "kind": "payments",
    },
    {
        "match": re.compile(r"phone|smartx|smartphone|mobile", re.I),
        "kind": "product",
        "productNames": ["SmartX Nova 5G Phone"],
    },
    {
        "match": re.compile(r"earbud|headphone|beatpro|audio", re.I),
        "kind": "product",
        "productNames": ["BeatPro Wireless Earbuds"],
    },
    {
        "match": re.compile(r"kitchen|kettle|aromabrew", re.I),
        "kind": "product",
        "productNames": ["AromaBrew Electric Kettle"],
    },
    {
        "match": re.compile(r"panjabi|fashion|clothes|shirt|jacket", re.I),
        "kind": "product",
        "productNames": ["Cotton Comfort Panjabi", "UrbanWalk Sneakers"],
    },
]


@st.cache_resource(show_spinner=False)
def _get_chatbot() -> RAGChatbot:
    return RAGChatbot()


def find_reply(
    text: str,
    history: list[tuple[str, str]] | None = None,
) -> dict:
    """
    Call the RAG pipeline and return a reply dict:
      {kind, text, sources, products?}

    *history* is a list of (user_text, assistant_text) pairs from prior turns.
    """
    chat_history = build_chat_history(history or [])
    try:
        response = _get_chatbot().ask(text, chat_history=chat_history)
    except Exception as exc:
        return {
            "kind": "text",
            "text": (
                "I'm having trouble connecting right now. "
                "Please contact our support team at support@shopsmartbd.com "
                "or call 09678-SMART (09678-76278)."
            ),
            "sources": [],
        }

    sources: list[str] = [
        s.get("title") or s.get("filename") or Path(s.get("source", "unknown")).name
        for s in response.formatted_sources()
    ]

    # Pick rich-card kind if the question matches a known visual topic.
    kind = "text"
    products: list[dict] | None = None
    for intent in _RICH_INTENTS:
        if intent["match"].search(text):
            kind = intent["kind"]
            if kind == "product" and intent.get("productNames"):
                products = [p for p in PRODUCTS if p["name"] in intent["productNames"]]
            break

    reply: dict = {"kind": kind, "text": response.answer, "sources": sources}
    if products is not None:
        reply["products"] = products
    return reply
