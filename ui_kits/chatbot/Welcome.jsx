const welcomeStyles = {
  wrap: {
    maxWidth: 720,
    margin: "0 auto",
    padding: "48px 24px 16px",
    textAlign: "center",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 16,
  },
  mark: {
    width: 76,
    height: 76,
    borderRadius: 22,
    background: "var(--bg-surface)",
    border: "1px solid var(--line)",
    boxShadow: "var(--e-2)",
    padding: 8,
    boxSizing: "border-box",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
  },
  sparkle: {
    position: "absolute",
    top: -8,
    right: -8,
    width: 28,
    height: 28,
    borderRadius: "50%",
    background: "var(--brand-saffron)",
    color: "#1F1B16",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  greet: {
    fontFamily: "var(--font-display)",
    fontWeight: 800,
    fontSize: 36,
    lineHeight: 1.08,
    letterSpacing: "-0.02em",
    color: "var(--ink-1)",
    margin: 0,
  },
  greetAccent: { color: "var(--brand-red)" },
  sub: {
    fontFamily: "var(--font-body)",
    fontSize: 16,
    lineHeight: 1.5,
    color: "var(--ink-2)",
    maxWidth: 480,
    margin: 0,
  },
  chips: {
    display: "flex",
    flexWrap: "wrap",
    gap: 8,
    justifyContent: "center",
    marginTop: 16,
    maxWidth: 600,
  },
  chip: {
    background: "var(--bg-surface)",
    border: "1px solid var(--line)",
    borderRadius: 999,
    padding: "8px 14px",
    fontSize: 13,
    fontWeight: 500,
    color: "var(--ink-1)",
    cursor: "pointer",
    transition: "all 160ms var(--ease)",
    fontFamily: "var(--font-body)",
  },
  hint: {
    display: "flex",
    alignItems: "center",
    gap: 14,
    marginTop: 28,
    color: "var(--ink-3)",
    fontSize: 12,
  },
  hintItem: { display: "inline-flex", alignItems: "center", gap: 6 },
  hintIcon: { color: "var(--brand-green)" },
};

function Welcome({ onPick }) {
  const { IconSparkle, IconShield, IconTruck, IconRotate } = window.SSIcons;
  const suggestions = window.SS.SUGGESTIONS;
  return (
    <div style={welcomeStyles.wrap}>
      <div style={welcomeStyles.mark}>
        <img src="../../assets/mark.svg" alt="" style={{ width: "100%", height: "100%" }} />
        <div style={welcomeStyles.sparkle}>
          <IconSparkle size={16} strokeWidth={2} />
        </div>
      </div>
      <h1 style={welcomeStyles.greet}>
        Hi, I'm <span style={welcomeStyles.greetAccent}>Shira</span>.
      </h1>
      <p style={welcomeStyles.sub}>
        Ask me about your order, delivery, returns, payments, or our products.
        I answer from our help docs, so every reply comes with sources.
      </p>
      <div style={welcomeStyles.chips}>
        {suggestions.map((s, i) => (
          <button
            key={i}
            style={welcomeStyles.chip}
            onClick={() => onPick(s)}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "var(--bg-soft)";
              e.currentTarget.style.borderColor = "var(--line-strong)";
              e.currentTarget.style.transform = "translateY(-1px)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "var(--bg-surface)";
              e.currentTarget.style.borderColor = "var(--line)";
              e.currentTarget.style.transform = "translateY(0)";
            }}
          >
            {s}
          </button>
        ))}
      </div>
      <div style={welcomeStyles.hint}>
        <span style={welcomeStyles.hintItem}>
          <span style={welcomeStyles.hintIcon}><IconTruck size={14} /></span> 3–7 day delivery
        </span>
        <span>·</span>
        <span style={welcomeStyles.hintItem}>
          <span style={welcomeStyles.hintIcon}><IconRotate size={14} /></span> 30-day returns
        </span>
        <span>·</span>
        <span style={welcomeStyles.hintItem}>
          <span style={welcomeStyles.hintIcon}><IconShield size={14} /></span> Authenticity guarantee
        </span>
      </div>
    </div>
  );
}

window.Welcome = Welcome;
