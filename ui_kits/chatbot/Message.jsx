const messageStyles = {
  row: { display: "flex", gap: 10, padding: "0 20px" },
  assist: { justifyContent: "flex-start", alignItems: "flex-start" },
  user: { justifyContent: "flex-end" },
  avatar: {
    width: 32, height: 32, borderRadius: "50%",
    background: "var(--bg-surface)", border: "1px solid var(--line)",
    padding: 2, boxSizing: "border-box", flexShrink: 0, marginTop: 2,
  },
  stack: { display: "flex", flexDirection: "column", maxWidth: "min(80%, 560px)", gap: 6 },
  bubbleAssist: {
    background: "var(--bg-sunken)", color: "var(--ink-1)",
    padding: "10px 14px", borderRadius: 14, borderBottomLeftRadius: 4,
    fontSize: 15, lineHeight: 1.5, fontFamily: "var(--font-body)",
    whiteSpace: "pre-wrap", wordBreak: "break-word",
  },
  bubbleUser: {
    background: "var(--brand-red)", color: "#fff",
    padding: "10px 14px", borderRadius: 14, borderBottomRightRadius: 4,
    fontSize: 15, lineHeight: 1.5, fontFamily: "var(--font-body)",
    whiteSpace: "pre-wrap", wordBreak: "break-word",
  },
  sourceToggle: {
    alignSelf: "flex-start",
    display: "inline-flex", alignItems: "center", gap: 6,
    background: "transparent", border: 0, cursor: "pointer",
    color: "var(--ink-3)", fontSize: 12, fontWeight: 600, padding: 0,
    fontFamily: "var(--font-body)",
  },
  sourceDot: { width: 6, height: 6, borderRadius: "50%", background: "var(--brand-red)" },
  sourcePanel: {
    background: "var(--bg-soft)", border: "1px solid var(--line)",
    borderRadius: 10, padding: "8px 12px", fontSize: 12, color: "var(--ink-2)",
    fontFamily: "var(--font-mono)", lineHeight: 1.6,
    display: "flex", flexDirection: "column", gap: 2,
  },
  typingBubble: {
    background: "var(--bg-sunken)",
    padding: "12px 16px", borderRadius: 14, borderBottomLeftRadius: 4,
    display: "flex", gap: 5, alignItems: "center",
  },
  typingDot: {
    width: 7, height: 7, borderRadius: "50%", background: "var(--ink-3)",
    animation: "ss-typing 1.2s var(--ease) infinite",
  },
};

function Message({ msg }) {
  const [openSources, setOpenSources] = React.useState(false);
  const { IconChevronDown, IconChevronUp } = window.SSIcons;
  const { ProductCard, PaymentRow, DeliveryCard } = window;

  if (msg.role === "user") {
    return (
      <div className="ss-row-in" style={{ ...messageStyles.row, ...messageStyles.user }}>
        <div style={messageStyles.stack}>
          <div style={messageStyles.bubbleUser}>{msg.text}</div>
        </div>
      </div>
    );
  }

  if (msg.role === "typing") {
    return (
      <div className="ss-row-in" style={{ ...messageStyles.row, ...messageStyles.assist }}>
        <img src="../../assets/shira-avatar.svg" alt="" style={messageStyles.avatar} />
        <div style={messageStyles.stack}>
          <div style={messageStyles.typingBubble}>
            <span style={{ ...messageStyles.typingDot, animationDelay: "0s" }} />
            <span style={{ ...messageStyles.typingDot, animationDelay: "0.15s" }} />
            <span style={{ ...messageStyles.typingDot, animationDelay: "0.3s" }} />
          </div>
        </div>
      </div>
    );
  }

  // assistant
  return (
    <div className="ss-row-in" style={{ ...messageStyles.row, ...messageStyles.assist }}>
      <img src="../../assets/shira-avatar.svg" alt="" style={messageStyles.avatar} />
      <div style={messageStyles.stack}>
        <div style={messageStyles.bubbleAssist}>{msg.text}</div>

        {msg.kind === "delivery" && <DeliveryCard />}
        {msg.kind === "payments" && <PaymentRow />}
        {msg.kind === "product" && msg.products && (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {msg.products.map((p) => <ProductCard key={p.name} product={p} />)}
          </div>
        )}

        {msg.sources && msg.sources.length > 0 && (
          <>
            <button
              style={messageStyles.sourceToggle}
              onClick={() => setOpenSources((v) => !v)}
            >
              <span style={messageStyles.sourceDot} />
              {msg.sources.length} source{msg.sources.length > 1 ? "s" : ""}
              {openSources ? <IconChevronUp size={14} /> : <IconChevronDown size={14} />}
            </button>
            {openSources && (
              <div style={messageStyles.sourcePanel}>
                {msg.sources.map((s, i) => (
                  <div key={i}>· {s}</div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

window.Message = Message;
