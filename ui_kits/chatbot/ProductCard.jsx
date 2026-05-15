const productCardStyles = {
  card: {
    display: "flex",
    gap: 12,
    background: "var(--bg-surface)",
    border: "1px solid var(--line)",
    borderRadius: 12,
    padding: 12,
    marginTop: 8,
    maxWidth: 360,
    boxShadow: "var(--e-1)",
  },
  photo: {
    width: 72,
    height: 72,
    flexShrink: 0,
    borderRadius: 8,
    background: "var(--bg-sunken)",
    backgroundImage: "url(../../assets/photos/placeholder.svg)",
    backgroundSize: "cover",
    backgroundPosition: "center",
  },
  body: { flex: 1, minWidth: 0, display: "flex", flexDirection: "column", gap: 4 },
  name: {
    fontFamily: "var(--font-display)",
    fontWeight: 700,
    fontSize: 14,
    color: "var(--ink-1)",
    lineHeight: 1.25,
  },
  blurb: {
    fontSize: 12,
    color: "var(--ink-3)",
    lineHeight: 1.4,
    display: "-webkit-box",
    WebkitLineClamp: 2,
    WebkitBoxOrient: "vertical",
    overflow: "hidden",
  },
  row: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: "auto",
    gap: 8,
  },
  price: {
    fontFamily: "var(--font-display)",
    fontWeight: 700,
    fontSize: 14,
    color: "var(--ink-1)",
  },
  chip: {
    display: "inline-flex",
    alignItems: "center",
    gap: 4,
    fontSize: 10,
    fontWeight: 600,
    padding: "2px 8px",
    borderRadius: 999,
    letterSpacing: "0.02em",
  },
  dot: { width: 5, height: 5, borderRadius: "50%" },
};

function ProductCard({ product }) {
  const tone = {
    in: { bg: "var(--success-bg)", fg: "var(--success)", label: "In stock" },
    low: { bg: "var(--warn-bg)", fg: "#8B5A0B", label: `Low${product.stockNote ? " — " + product.stockNote : ""}` },
    out: { bg: "var(--error-bg)", fg: "var(--error)", label: "Out of stock" },
  }[product.stock];
  return (
    <div style={productCardStyles.card}>
      <div style={productCardStyles.photo} />
      <div style={productCardStyles.body}>
        <div style={productCardStyles.name}>{product.name}</div>
        <div style={productCardStyles.blurb}>{product.blurb}</div>
        <div style={productCardStyles.row}>
          <span style={productCardStyles.price}>
            BDT {product.price.toLocaleString("en-US")}
          </span>
          <span style={{ ...productCardStyles.chip, background: tone.bg, color: tone.fg }}>
            <span style={{ ...productCardStyles.dot, background: tone.fg }} />
            {tone.label}
          </span>
        </div>
      </div>
    </div>
  );
}

window.ProductCard = ProductCard;
