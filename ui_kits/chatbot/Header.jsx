const headerStyles = {
  wrap: {
    position: "sticky",
    top: 0,
    zIndex: 5,
    background: "rgba(251,248,243,0.88)",
    backdropFilter: "blur(10px)",
    WebkitBackdropFilter: "blur(10px)",
    borderBottom: "1px solid var(--line)",
  },
  inner: {
    maxWidth: 820,
    margin: "0 auto",
    padding: "12px 20px",
    display: "flex",
    alignItems: "center",
    gap: 12,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: "50%",
    background: "var(--bg-surface)",
    border: "1px solid var(--line)",
    padding: 3,
    boxSizing: "border-box",
    flexShrink: 0,
  },
  id: { display: "flex", flexDirection: "column", lineHeight: 1.1, flex: 1, minWidth: 0 },
  name: {
    fontFamily: "var(--font-display)",
    fontWeight: 800,
    fontSize: 16,
    color: "var(--ink-1)",
    letterSpacing: "-0.01em",
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  status: {
    fontSize: 12,
    color: "var(--ink-3)",
    marginTop: 2,
    display: "flex",
    alignItems: "center",
    gap: 6,
  },
  dot: {
    width: 7,
    height: 7,
    borderRadius: "50%",
    background: "var(--brand-green)",
    boxShadow: "0 0 0 3px rgba(14,140,90,0.18)",
  },
  brand: {
    fontFamily: "var(--font-display)",
    fontWeight: 800,
    fontSize: 12,
    color: "var(--brand-red)",
    letterSpacing: "0.02em",
    padding: "3px 8px",
    background: "#FBE3E5",
    borderRadius: 999,
  },
  actions: { display: "flex", gap: 6 },
  iconBtn: {
    width: 36,
    height: 36,
    borderRadius: 8,
    background: "transparent",
    border: "1px solid transparent",
    color: "var(--ink-2)",
    cursor: "pointer",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "background 120ms var(--ease)",
  },
};

function Header({ onReset, hasMessages }) {
  const { IconRotate, IconClose } = window.SSIcons;
  return (
    <header style={headerStyles.wrap}>
      <div style={headerStyles.inner}>
        <img style={headerStyles.avatar} src="../../assets/shira-avatar.svg" alt="" />
        <div style={headerStyles.id}>
          <div style={headerStyles.name}>
            Shira <span style={headerStyles.brand}>ShopSmart BD</span>
          </div>
          <div style={headerStyles.status}>
            <span style={headerStyles.dot} />
            Online · usually replies instantly
          </div>
        </div>
        <div style={headerStyles.actions}>
          {hasMessages && (
            <button
              style={headerStyles.iconBtn}
              onClick={onReset}
              onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg-soft)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
              title="Reset chat"
            >
              <IconRotate size={18} />
            </button>
          )}
        </div>
      </div>
    </header>
  );
}

window.Header = Header;
