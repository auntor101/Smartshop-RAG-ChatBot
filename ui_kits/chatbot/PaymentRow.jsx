const paymentRowStyles = {
  wrap: { marginTop: 10, display: "flex", flexDirection: "column", gap: 8, maxWidth: 420 },
  row: { display: "flex", flexWrap: "wrap", gap: 6 },
  chip: {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    padding: "6px 10px",
    background: "var(--bg-surface)",
    border: "1px solid var(--line)",
    borderRadius: 999,
    fontSize: 12,
    fontWeight: 600,
    color: "var(--ink-1)",
  },
  img: { height: 18, display: "block" },
};

const PAYMENTS = [
  { src: "../../assets/payments/bkash.svg", alt: "bKash" },
  { src: "../../assets/payments/nagad.svg", alt: "Nagad" },
  { src: "../../assets/payments/visa.svg", alt: "Visa" },
  { src: "../../assets/payments/mastercard.svg", alt: "Mastercard" },
  { src: "../../assets/payments/paypal.svg", alt: "PayPal" },
  { src: "../../assets/payments/cod.svg", alt: "Cash on Delivery" },
];

function PaymentRow() {
  return (
    <div style={paymentRowStyles.wrap}>
      <div style={paymentRowStyles.row}>
        {PAYMENTS.map((p) => (
          <span key={p.alt} style={paymentRowStyles.chip}>
            <img src={p.src} alt={p.alt} style={paymentRowStyles.img} />
          </span>
        ))}
      </div>
    </div>
  );
}

window.PaymentRow = PaymentRow;
