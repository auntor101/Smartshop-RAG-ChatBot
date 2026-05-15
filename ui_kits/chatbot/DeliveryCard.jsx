const deliveryCardStyles = {
  card: {
    marginTop: 10,
    display: "flex",
    alignItems: "center",
    gap: 14,
    background: "var(--bg-surface)",
    border: "1px solid var(--line)",
    borderRadius: 12,
    padding: 12,
    maxWidth: 380,
    boxShadow: "var(--e-1)",
  },
  illus: { width: 76, height: 56, flexShrink: 0 },
  rows: { display: "flex", flexDirection: "column", gap: 4, flex: 1 },
  row: { display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12 },
  label: { fontSize: 11, color: "var(--ink-3)", textTransform: "uppercase", letterSpacing: "0.04em", fontWeight: 600 },
  val: { fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 14, color: "var(--ink-1)" },
};

function DeliveryCard() {
  return (
    <div style={deliveryCardStyles.card}>
      <img src="../../assets/illustrations/delivery.svg" alt="" style={deliveryCardStyles.illus} />
      <div style={deliveryCardStyles.rows}>
        <div style={deliveryCardStyles.row}>
          <span style={deliveryCardStyles.label}>Standard</span>
          <span style={deliveryCardStyles.val}>3–7 days</span>
        </div>
        <div style={deliveryCardStyles.row}>
          <span style={deliveryCardStyles.label}>Express</span>
          <span style={deliveryCardStyles.val}>1–2 days</span>
        </div>
        <div style={deliveryCardStyles.row}>
          <span style={deliveryCardStyles.label}>Free over</span>
          <span style={deliveryCardStyles.val}>BDT 1,000</span>
        </div>
      </div>
    </div>
  );
}

window.DeliveryCard = DeliveryCard;
