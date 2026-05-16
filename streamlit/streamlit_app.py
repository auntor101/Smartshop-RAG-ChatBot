"""
ShopSmart BD — Shira Chatbot
Streamlit-native chat interface.

Local:  streamlit run streamlit/streamlit_app.py   (from project root)
Cloud:  push to GitHub → connect on share.streamlit.io
"""
import base64
import os
from pathlib import Path
from typing import Optional

# Windows + Streamlit: tqdm / HuggingFace progress bars flush stderr in ways
# that raise OSError on Windows. Disable before importing heavy libs.
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import streamlit as st

from responses import find_reply, SUGGESTIONS

# ─────────────────────────────────────────────────────────────────────────────
# Page config (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ShopSmart BD — Chat with Shira",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# Asset helpers
# ─────────────────────────────────────────────────────────────────────────────
HERE = Path(__file__).parent


def _b64(rel: str) -> str:
    """Return a base64 data-URI for an asset file, or '' if missing."""
    p = HERE / rel
    if not p.exists():
        return ""
    raw = p.read_bytes()
    ext = p.suffix.lstrip(".")
    mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


# Pre-load brand assets as data-URIs (portable across local + Streamlit Cloud)
SHIRA_URI   = _b64("assets/shira-avatar.svg")
MARK_URI    = _b64("assets/mark.svg")
DELIVERY_URI = _b64("assets/illustrations/delivery.svg")
PLACEHOLDER_URI = _b64("assets/photos/placeholder.svg")

PAYMENT_URIS: dict[str, str] = {
    "bKash":            _b64("assets/payments/bkash.svg"),
    "Nagad":            _b64("assets/payments/nagad.svg"),
    "Visa":             _b64("assets/payments/visa.svg"),
    "Mastercard":       _b64("assets/payments/mastercard.svg"),
    "PayPal":           _b64("assets/payments/paypal.svg"),
    "Cash on Delivery": _b64("assets/payments/cod.svg"),
}

# Avatar: use SVG file path when it exists (Streamlit renders it natively),
# fall back to the brand emoji.
_AVATAR_PATH = HERE / "assets/shira-avatar.svg"
AVATAR_ARG: str = str(_AVATAR_PATH) if _AVATAR_PATH.exists() else "🛍️"

# ─────────────────────────────────────────────────────────────────────────────
# CSS injection — design tokens + Streamlit overrides
# ─────────────────────────────────────────────────────────────────────────────
def _inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Design tokens ─────────────────────────────────────── */
:root {
  --brand-red:    #E63946;
  --brand-red-h:  #D62F3C;
  --brand-green:  #0E8C5A;
  --brand-saffron:#F5A524;
  --bg-canvas:    #FBF8F3;
  --bg-surface:   #FFFFFF;
  --bg-sunken:    #F2EDE4;
  --bg-soft:      #F7F2E9;
  --ink-1:        #1F1B16;
  --ink-2:        #4A453E;
  --ink-3:        #7A736A;
  --ink-4:        #A8A095;
  --line:         #E8E0D2;
  --line-strong:  #D6CCB5;
  --success:      #0E8C5A;
  --success-bg:   #E2F1E8;
  --warn-bg:      #FCEDD2;
  --warn-fg:      #8B5A0B;
  --error:        #E63946;
  --error-bg:     #FBE3E5;
  --f-display:    'Manrope', system-ui, sans-serif;
  --f-body:       'Source Sans 3', system-ui, sans-serif;
  --f-mono:       'JetBrains Mono', monospace;
  --e-1:          0 1px 2px rgba(31,27,22,.06);
  --e-2:          0 4px 12px rgba(31,27,22,.08);
  --ease:         cubic-bezier(.2,.7,.2,1);
}

/* ── App shell ─────────────────────────────────────────── */
.stApp {
  background: var(--bg-canvas) !important;
  font-family: var(--f-body) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { display: none; }
.stDeployButton { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* Main block */
.main .block-container {
  padding-top: 0 !important;
  padding-bottom: 120px !important;
  max-width: 860px !important;
}

/* ── Chat messages ─────────────────────────────────────── */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  padding: 4px 0 !important;
  gap: 10px !important;
}

/* Widen the content area */
[data-testid="stChatMessageContent"] {
  max-width: calc(100% - 50px) !important;
}

/* Assistant bubble */
[data-testid="stChatMessage"]:has(img[alt="assistant avatar"]),
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
  align-items: flex-start !important;
}

/* User bubble background */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
  [data-testid="stMarkdownContainer"] > p {
  background: var(--brand-red) !important;
  color: #fff !important;
  border-radius: 14px !important;
  border-bottom-right-radius: 4px !important;
  padding: 10px 14px !important;
  font-size: 15px !important;
  line-height: 1.5 !important;
  display: inline-block !important;
}

/* ── Chat input ────────────────────────────────────────── */
[data-testid="stChatInput"] {
  border-top: 1px solid var(--line) !important;
  background: linear-gradient(180deg, transparent 0%, var(--bg-canvas) 30%) !important;
  padding: 12px 16px 16px !important;
}

[data-testid="stChatInput"] textarea {
  background: var(--bg-surface) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  font-family: var(--f-body) !important;
  font-size: 15px !important;
  color: var(--ink-1) !important;
  box-shadow: var(--e-2) !important;
}

[data-testid="stChatInput"] textarea:focus {
  border-color: var(--brand-red) !important;
  box-shadow: var(--e-2), 0 0 0 3px var(--error-bg) !important;
  outline: none !important;
}

[data-testid="stChatInput"] button {
  background: var(--brand-red) !important;
  border-radius: 10px !important;
  color: #fff !important;
}

[data-testid="stChatInput"] button:hover {
  background: var(--brand-red-h) !important;
}

/* ── Suggestion chips ──────────────────────────────────── */
.ss-chips [data-testid="stButton"] > button {
  background: var(--bg-surface) !important;
  border: 1px solid var(--line) !important;
  border-radius: 999px !important;
  color: var(--ink-1) !important;
  font-family: var(--f-body) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 6px 14px !important;
  height: auto !important;
  min-height: unset !important;
  line-height: 1.4 !important;
  transition: all 160ms var(--ease) !important;
  white-space: normal !important;
  text-align: center !important;
  box-shadow: var(--e-1) !important;
}

.ss-chips [data-testid="stButton"] > button:hover {
  background: var(--bg-soft) !important;
  border-color: var(--line-strong) !important;
  transform: translateY(-1px) !important;
  box-shadow: var(--e-2) !important;
}

.ss-chips [data-testid="stButton"] > button:active {
  transform: scale(0.98) !important;
}

/* ── Source expander ───────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--bg-soft) !important;
  border: 1px solid var(--line) !important;
  border-radius: 8px !important;
  overflow: hidden !important;
}

[data-testid="stExpander"] summary {
  font-size: 12px !important;
  color: var(--ink-3) !important;
  font-weight: 600 !important;
  font-family: var(--f-body) !important;
}

[data-testid="stExpander"] summary:hover {
  color: var(--ink-1) !important;
}

/* Inline code (source citations) */
code {
  font-family: var(--f-mono) !important;
  background: var(--bg-sunken) !important;
  color: var(--ink-2) !important;
  border-radius: 4px !important;
  padding: 1px 6px !important;
  font-size: 12px !important;
}

/* ── Scrollbar ─────────────────────────────────────────── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb {
  background: var(--line);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover { background: var(--line-strong); }
::-webkit-scrollbar-track { background: transparent; }
</style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Rich-content HTML builders
# ─────────────────────────────────────────────────────────────────────────────
def _product_card_html(product: dict) -> str:
    tones: dict[str, tuple[str, str, str]] = {
        "in":  ("#E2F1E8", "#0E8C5A", "In stock"),
        "low": ("#FCEDD2", "#8B5A0B",
                "Low" + (f" — {product['stockNote']}" if product.get("stockNote") else "")),
        "out": ("#FBE3E5", "#E63946", "Out of stock"),
    }
    bg, fg, label = tones.get(product.get("stock", "out"), tones["out"])
    price = f"BDT {product['price']:,}"
    bg_photo = (
        f'background-image:url("{PLACEHOLDER_URI}");background-size:cover;'
        if PLACEHOLDER_URI
        else ""
    )
    return f"""
<div style="display:flex;gap:12px;background:#fff;border:1px solid #E8E0D2;
            border-radius:12px;padding:12px;max-width:380px;
            box-shadow:0 1px 2px rgba(31,27,22,.06);margin-top:8px;
            font-family:'Source Sans 3',system-ui,sans-serif;">
  <div style="width:72px;height:72px;flex-shrink:0;border-radius:8px;
              background:#F2EDE4;{bg_photo}background-position:center;"></div>
  <div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:4px;">
    <div style="font-family:'Manrope',system-ui,sans-serif;font-weight:700;
                font-size:14px;color:#1F1B16;line-height:1.25;">
      {product["name"]}
    </div>
    <div style="font-size:12px;color:#7A736A;line-height:1.4;
                overflow:hidden;display:-webkit-box;
                -webkit-line-clamp:2;-webkit-box-orient:vertical;">
      {product["blurb"]}
    </div>
    <div style="display:flex;align-items:center;justify-content:space-between;
                margin-top:auto;gap:8px;">
      <span style="font-family:'Manrope',system-ui,sans-serif;font-weight:700;
                   font-size:14px;color:#1F1B16;">{price}</span>
      <span style="display:inline-flex;align-items:center;gap:4px;font-size:10px;
                   font-weight:600;padding:2px 8px;border-radius:999px;
                   background:{bg};color:{fg};letter-spacing:.02em;">
        <span style="width:5px;height:5px;border-radius:50%;
                     background:{fg};display:inline-block;"></span>
        {label}
      </span>
    </div>
  </div>
</div>"""


def _payment_row_html() -> str:
    chips = ""
    for name, uri in PAYMENT_URIS.items():
        inner = (
            f'<img src="{uri}" alt="{name}" style="height:18px;display:block;"/>'
            if uri
            else f'<span style="font-size:11px;">{name}</span>'
        )
        chips += (
            f'<span style="display:inline-flex;align-items:center;gap:8px;'
            f'padding:6px 10px;background:#fff;border:1px solid #E8E0D2;'
            f'border-radius:999px;font-size:12px;font-weight:600;color:#1F1B16;">'
            f'{inner}</span>'
        )
    return (
        f'<div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:6px;">'
        f'{chips}</div>'
    )


def _delivery_card_html() -> str:
    img_tag = (
        f'<img src="{DELIVERY_URI}" alt="" style="width:76px;height:56px;flex-shrink:0;"/>'
        if DELIVERY_URI
        else ""
    )
    rows = [("Standard", "3–7 days"), ("Express", "1–2 days"), ("Free over", "BDT 1,000")]
    rows_html = "".join(
        f'<div style="display:flex;align-items:baseline;justify-content:space-between;gap:12px;">'
        f'<span style="font-size:11px;color:#7A736A;text-transform:uppercase;'
        f'letter-spacing:.04em;font-weight:600;">{lbl}</span>'
        f'<span style="font-family:\'Manrope\',system-ui,sans-serif;font-weight:700;'
        f'font-size:14px;color:#1F1B16;">{val}</span></div>'
        for lbl, val in rows
    )
    return (
        f'<div style="margin-top:10px;display:flex;align-items:center;gap:14px;'
        f'background:#fff;border:1px solid #E8E0D2;border-radius:12px;padding:12px;'
        f'max-width:380px;box-shadow:0 1px 2px rgba(31,27,22,.06);'
        f'font-family:\'Source Sans 3\',system-ui,sans-serif;">'
        f'{img_tag}'
        f'<div style="display:flex;flex-direction:column;gap:4px;flex:1;">'
        f'{rows_html}</div></div>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
def _render_header() -> None:
    avatar_html = (
        f'<img src="{SHIRA_URI}" style="width:40px;height:40px;border-radius:50%;'
        f'background:#fff;border:1px solid #E8E0D2;padding:3px;'
        f'box-sizing:border-box;flex-shrink:0;" alt="Shira"/>'
        if SHIRA_URI
        else '<div style="width:40px;height:40px;border-radius:50%;background:#E63946;flex-shrink:0;"></div>'
    )
    st.markdown(
        f"""
<div style="position:sticky;top:0;z-index:100;
            background:rgba(251,248,243,.92);
            backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
            border-bottom:1px solid #E8E0D2;
            padding:12px 20px;margin:-1rem -1rem 1rem -1rem;
            display:flex;align-items:center;gap:12px;">
  {avatar_html}
  <div style="display:flex;flex-direction:column;line-height:1.1;flex:1;min-width:0;">
    <div style="font-family:'Manrope',system-ui,sans-serif;font-weight:800;
                font-size:16px;color:#1F1B16;letter-spacing:-.01em;
                display:flex;align-items:center;gap:8px;">
      Shira
      <span style="font-family:'Manrope',system-ui,sans-serif;font-weight:800;
                   font-size:12px;color:#E63946;letter-spacing:.02em;
                   padding:3px 8px;background:#FBE3E5;border-radius:999px;">
        ShopSmart BD
      </span>
    </div>
    <div style="font-size:12px;color:#7A736A;margin-top:2px;
                display:flex;align-items:center;gap:6px;
                font-family:'Source Sans 3',system-ui,sans-serif;">
      <span style="width:7px;height:7px;border-radius:50%;background:#0E8C5A;
                   box-shadow:0 0 0 3px rgba(14,140,90,.18);
                   display:inline-block;"></span>
      Online · usually replies instantly
    </div>
  </div>
</div>""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Welcome screen
# ─────────────────────────────────────────────────────────────────────────────
def _render_welcome() -> Optional[str]:
    """Render the empty-state hero. Returns a suggestion string if a chip was clicked."""
    mark_img = (
        f'<img src="{MARK_URI}" alt="" style="width:100%;height:100%;"/>'
        if MARK_URI
        else '<div style="width:100%;height:100%;background:#E63946;border-radius:12px;"></div>'
    )
    st.markdown(
        f"""
<div style="max-width:680px;margin:0 auto;padding:48px 24px 8px;text-align:center;">
  <!-- Brand mark -->
  <div style="width:76px;height:76px;border-radius:22px;background:#fff;
              border:1px solid #E8E0D2;box-shadow:0 4px 12px rgba(31,27,22,.08);
              padding:8px;box-sizing:border-box;display:inline-flex;
              align-items:center;justify-content:center;position:relative;
              margin-bottom:20px;">
    {mark_img}
    <div style="position:absolute;top:-8px;right:-8px;width:28px;height:28px;
                border-radius:50%;background:#F5A524;color:#1F1B16;
                display:flex;align-items:center;justify-content:center;
                font-size:14px;font-weight:700;">✦</div>
  </div>

  <!-- Greeting -->
  <h1 style="font-family:'Manrope',system-ui,sans-serif;font-weight:800;
             font-size:clamp(28px,5vw,38px);line-height:1.08;
             letter-spacing:-.02em;color:#1F1B16;margin:0 0 12px;">
    Hi, I'm <span style="color:#E63946;">Shira</span>.
  </h1>
  <p style="font-family:'Source Sans 3',system-ui,sans-serif;font-size:16px;
            line-height:1.5;color:#4A453E;max-width:460px;margin:0 auto 20px;">
    Ask me about your order, delivery, returns, payments, or our products.
    I answer from our help docs, so every reply comes with sources.
  </p>

  <!-- Trust signals -->
  <div style="display:flex;align-items:center;justify-content:center;
              flex-wrap:wrap;gap:12px 18px;color:#7A736A;font-size:12px;
              font-family:'Source Sans 3',system-ui,sans-serif;margin-bottom:32px;">
    <span>🚚&nbsp; 3–7 day delivery</span>
    <span style="color:#D6CCB5;">·</span>
    <span>🔄&nbsp; 30-day returns</span>
    <span style="color:#D6CCB5;">·</span>
    <span>🛡&nbsp; Authenticity guarantee</span>
  </div>

  <p style="font-size:13px;color:#7A736A;margin:0 0 10px;
            font-family:'Source Sans 3',system-ui,sans-serif;">
    Quick questions to get started:
  </p>
</div>""",
        unsafe_allow_html=True,
    )

    # Suggestion chips — rendered as Streamlit buttons inside a CSS-targeted div
    st.markdown('<div class="ss-chips">', unsafe_allow_html=True)
    clicked: Optional[str] = None
    cols = st.columns(len(SUGGESTIONS), gap="small")
    for i, suggestion in enumerate(SUGGESTIONS):
        with cols[i]:
            if st.button(suggestion, key=f"chip_{i}", use_container_width=True):
                clicked = suggestion
    st.markdown("</div>", unsafe_allow_html=True)

    return clicked


# ─────────────────────────────────────────────────────────────────────────────
# Message rendering helpers
# ─────────────────────────────────────────────────────────────────────────────
def _render_reply_body(reply: dict) -> None:
    """Render assistant reply content inside an active st.chat_message block."""
    st.markdown(reply.get("text", ""))

    kind = reply.get("kind", "text")
    if kind == "delivery":
        st.markdown(_delivery_card_html(), unsafe_allow_html=True)
    elif kind == "payments":
        st.markdown(_payment_row_html(), unsafe_allow_html=True)
    elif kind == "product" and reply.get("products"):
        for product in reply["products"]:
            st.markdown(_product_card_html(product), unsafe_allow_html=True)

    sources = reply.get("sources") or []
    if sources:
        n = len(sources)
        label = f"{'📄 '}{n} source{'s' if n > 1 else ''}"
        with st.expander(label):
            for src in sources:
                st.markdown(f"`{src}`")


def _render_history() -> None:
    """Re-render every message from session_state."""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["text"])
        else:
            with st.chat_message("assistant", avatar=AVATAR_ARG):
                _render_reply_body(msg)


# ─────────────────────────────────────────────────────────────────────────────
# History builder
# ─────────────────────────────────────────────────────────────────────────────
def _build_history() -> list[tuple[str, str]]:
    """Return (user_text, assistant_text) pairs from the current session."""
    pairs: list[tuple[str, str]] = []
    msgs = st.session_state.messages
    for i in range(0, len(msgs) - 1, 2):
        u, a = msgs[i], msgs[i + 1]
        if u["role"] == "user" and a["role"] == "assistant":
            pairs.append((u["text"], a["text"]))
    return pairs


# ─────────────────────────────────────────────────────────────────────────────
# Send handler
# ─────────────────────────────────────────────────────────────────────────────
def _handle_send(text: str) -> None:
    """Display user + assistant messages inline and persist to session_state."""
    history = _build_history()

    # User turn
    with st.chat_message("user"):
        st.markdown(text)
    st.session_state.messages.append({"role": "user", "text": text})

    # Assistant turn — RAG provides real latency, no artificial sleep needed
    with st.chat_message("assistant", avatar=AVATAR_ARG):
        with st.spinner("Thinking…"):
            reply = find_reply(text, history)
        _render_reply_body(reply)

    st.session_state.messages.append({"role": "assistant", **reply})


# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─────────────────────────────────────────────────────────────────────────────
# App layout
# ─────────────────────────────────────────────────────────────────────────────
_inject_css()
_render_header()

if st.session_state.messages:
    # Conversation in progress — show history
    _render_history()
else:
    # Empty state — show welcome + suggestion chips
    picked = _render_welcome()
    if picked:
        _handle_send(picked)

# Sticky chat input (always rendered at bottom by Streamlit)
if prompt := st.chat_input("Ask about your order, returns, payments…"):
    _handle_send(prompt)
