const composerStyles = {
  wrap: {
    position: "sticky",
    bottom: 0,
    background: "linear-gradient(180deg, rgba(251,248,243,0) 0%, var(--bg-canvas) 28%, var(--bg-canvas) 100%)",
    paddingBottom: "max(16px, env(safe-area-inset-bottom))",
    paddingTop: 14,
    zIndex: 4,
  },
  inner: { maxWidth: 820, margin: "0 auto", padding: "0 16px" },
  hints: { display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 10 },
  hintChip: {
    background: "var(--bg-surface)",
    border: "1px solid var(--line)",
    borderRadius: 999,
    padding: "5px 10px",
    fontSize: 12,
    fontWeight: 500,
    color: "var(--ink-2)",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
    transition: "all 120ms var(--ease)",
  },
  box: {
    display: "flex",
    alignItems: "flex-end",
    gap: 8,
    background: "var(--bg-surface)",
    border: "1px solid var(--line)",
    borderRadius: 16,
    padding: "6px 6px 6px 14px",
    boxShadow: "var(--e-2)",
    transition: "border-color 160ms var(--ease), box-shadow 160ms var(--ease)",
  },
  textarea: {
    flex: 1,
    minHeight: 36,
    maxHeight: 140,
    border: 0,
    outline: 0,
    background: "transparent",
    resize: "none",
    fontFamily: "var(--font-body)",
    fontSize: 15,
    lineHeight: 1.45,
    color: "var(--ink-1)",
    padding: "8px 0",
  },
  send: {
    width: 40, height: 40, borderRadius: 12,
    background: "var(--brand-red)", color: "#fff",
    border: 0, cursor: "pointer",
    display: "inline-flex", alignItems: "center", justifyContent: "center",
    transition: "background 120ms var(--ease), transform 120ms var(--ease)",
    flexShrink: 0,
  },
  sendDisabled: {
    background: "var(--bg-sunken)", color: "var(--ink-4)", cursor: "not-allowed",
  },
  foot: {
    textAlign: "center",
    fontSize: 11,
    color: "var(--ink-4)",
    marginTop: 8,
    fontFamily: "var(--font-body)",
  },
};

function Composer({ onSend, showHints }) {
  const [value, setValue] = React.useState("");
  const taRef = React.useRef(null);
  const { IconSend } = window.SSIcons;

  const auto = () => {
    const el = taRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(140, el.scrollHeight) + "px";
  };

  const submit = () => {
    const t = value.trim();
    if (!t) return;
    onSend(t);
    setValue("");
    requestAnimationFrame(auto);
  };

  const onKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const onFocus = (e) => {
    e.currentTarget.parentElement.style.borderColor = "var(--brand-red)";
    e.currentTarget.parentElement.style.boxShadow = "var(--e-2), 0 0 0 3px var(--error-bg)";
  };
  const onBlur = (e) => {
    e.currentTarget.parentElement.style.borderColor = "var(--line)";
    e.currentTarget.parentElement.style.boxShadow = "var(--e-2)";
  };

  const canSend = value.trim().length > 0;

  return (
    <div style={composerStyles.wrap}>
      <div style={composerStyles.inner}>
        {showHints && (
          <div style={composerStyles.hints}>
            {["Track my order", "Return policy", "bKash payment", "Warranty"].map((t) => (
              <button
                key={t}
                style={composerStyles.hintChip}
                onClick={() => onSend(t)}
                onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg-soft)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "var(--bg-surface)")}
              >
                {t}
              </button>
            ))}
          </div>
        )}
        <div style={composerStyles.box}>
          <textarea
            ref={taRef}
            style={composerStyles.textarea}
            placeholder="Ask about your order, returns, payments…"
            value={value}
            rows={1}
            onChange={(e) => { setValue(e.target.value); auto(); }}
            onKeyDown={onKey}
            onFocus={onFocus}
            onBlur={onBlur}
          />
          <button
            style={{ ...composerStyles.send, ...(canSend ? {} : composerStyles.sendDisabled) }}
            onClick={submit}
            disabled={!canSend}
            aria-label="Send"
            onMouseDown={(e) => canSend && (e.currentTarget.style.transform = "scale(0.95)")}
            onMouseUp={(e) => canSend && (e.currentTarget.style.transform = "scale(1)")}
            onMouseLeave={(e) => canSend && (e.currentTarget.style.transform = "scale(1)")}
          >
            <IconSend size={18} strokeWidth={2} />
          </button>
        </div>
        <div style={composerStyles.foot}>
          Shira answers from <code className="mono">data/shopsmart_docs</code> · responses are grounded in citations
        </div>
      </div>
    </div>
  );
}

window.Composer = Composer;
