/* Canned responses keyed by intent, derived from data/shopsmart_docs/.
   No LLM call — deterministic for UI demo. */

const PRODUCTS = [
  { name: "SmartX Nova 5G Phone", price: 24990, category: "Electronics", stock: "in", warranty: "6 months", blurb: "Lightweight Android with bright AMOLED display, 128 GB, all-day battery." },
  { name: "BeatPro Wireless Earbuds", price: 3490, category: "Electronics", stock: "low", stockNote: "3 left", warranty: "6 months", blurb: "Touch controls, sweat-resistant, up to 24 hours with charging case." },
  { name: "VoltMate 20000mAh Power Bank", price: 2190, category: "Electronics", stock: "in", warranty: "6 months", blurb: "Dual USB output, fast charging, slim travel body." },
  { name: "HomeView HD Security Camera", price: 4590, category: "Electronics", stock: "out", warranty: "6 months", blurb: "Indoor Wi-Fi, 1080p, night vision, two-way audio." },
  { name: "Cotton Comfort Panjabi", price: 1450, category: "Fashion", stock: "in", warranty: "—", blurb: "Breathable cotton panjabi for festivals and office events." },
  { name: "UrbanWalk Sneakers", price: 2290, category: "Fashion", stock: "in", warranty: "—", blurb: "Cushioned soles, knitted upper, built for daily walking." },
  { name: "AromaBrew Electric Kettle", price: 1790, category: "Home & Kitchen", stock: "low", stockNote: "1 left", warranty: "6 months", blurb: "Stainless steel, auto shut-off, boil-dry protection." },
];

const SUGGESTIONS = [
  "How long does delivery take?",
  "Can I pay with bKash?",
  "What is your return policy?",
  "Show me phones under BDT 25,000",
  "How does the referral program work?",
];

const INTENTS = [
  {
    match: /track|tracking|where.*order|order.*status/i,
    kind: "text",
    text: "You can track your order using your order ID on the ShopSmart BD website. We also send SMS alerts when your order is confirmed, shipped, and out for delivery.",
    sources: ["faq.txt #6"],
  },
  {
    match: /deliver|shipping|how long|how soon|express|standard/i,
    kind: "delivery",
    text: "ShopSmart BD offers standard delivery in 3–7 business days and express delivery in 1–2 business days in eligible areas. Orders over BDT 1000 ship free. Is there anything else I can help you with?",
    sources: ["faq.txt #1", "faq.txt #3"],
  },
  {
    match: /bkash|nagad|pay|payment|cod|cash on delivery|visa|card/i,
    kind: "payments",
    text: "ShopSmart BD accepts Visa, Mastercard, bKash, Nagad, PayPal, and cash on delivery in Dhaka only. bKash refunds are usually processed within 2 hours after approval.",
    sources: ["faq.txt #13", "policies.txt — Refund Timeline"],
  },
  {
    match: /return|refund|exchange|30.day/i,
    kind: "text",
    text: "Most eligible items can be returned within 30 days of delivery. Returned items must be unused, unwashed, undamaged, and include the original tags, packaging, manuals, and accessories. Is there anything else I can help you with?",
    sources: ["policies.txt — Return Policy", "faq.txt #8"],
  },
  {
    match: /warranty/i,
    kind: "text",
    text: "Eligible electronics include a 6-month warranty unless a product page states a different official brand warranty. Eligible accessories include a 1-month warranty unless the product page states otherwise.",
    sources: ["faq.txt #24", "faq.txt #25"],
  },
  {
    match: /referral|refer.a.friend|invite/i,
    kind: "text",
    text: "You receive BDT 200 referral credit for each successful referral after the referred customer completes an eligible purchase.",
    sources: ["faq.txt #22"],
  },
  {
    match: /promo|coupon|discount|code/i,
    kind: "text",
    text: "Enter your promo code in the Promo Code box at checkout and click Apply before placing the order. Codes may expire, have minimum order values, or apply only to selected products.",
    sources: ["faq.txt #20", "faq.txt #21"],
  },
  {
    match: /phone|smartx|smartphone|mobile/i,
    kind: "product",
    text: "Here is what we have under BDT 25,000. The SmartX Nova 5G is currently in stock with a 6-month warranty.",
    productNames: ["SmartX Nova 5G Phone"],
    sources: ["products.txt #1"],
  },
  {
    match: /earbud|headphone|beatpro|audio/i,
    kind: "product",
    text: "BeatPro earbuds are running low — 3 left in stock as of this morning.",
    productNames: ["BeatPro Wireless Earbuds"],
    sources: ["products.txt #2"],
  },
  {
    match: /kitchen|kettle|aromabrew/i,
    kind: "product",
    text: "We have one AromaBrew kettle left. It has a 6-month warranty.",
    productNames: ["AromaBrew Electric Kettle"],
    sources: ["products.txt #13"],
  },
  {
    match: /panjabi|fashion|clothes|shirt|jacket/i,
    kind: "product",
    text: "Here is a popular pick from our Fashion collection.",
    productNames: ["Cotton Comfort Panjabi", "UrbanWalk Sneakers"],
    sources: ["products.txt #7", "products.txt #8"],
  },
  {
    match: /password|forgot|reset/i,
    kind: "text",
    text: "Click Forgot Password on the sign-in page and follow the reset link sent to your registered email address.",
    sources: ["faq.txt #17"],
  },
  {
    match: /hello|hi |hey|salam|hi$|namaskar/i,
    kind: "text",
    text: "Hi! I'm Shira, here to help with orders, returns, payments, and product questions. What can I help you with today?",
    sources: [],
  },
];

const FALLBACK = {
  kind: "text",
  text: "I don't have that information right now. Please contact our support team at support@shopsmartbd.com or call 09678-SMART (09678-76278).",
  sources: [],
};

function findReply(text) {
  const t = text.trim();
  for (const intent of INTENTS) {
    if (intent.match.test(t)) {
      const reply = { ...intent };
      if (reply.productNames) {
        reply.products = reply.productNames.map((n) => PRODUCTS.find((p) => p.name === n)).filter(Boolean);
      }
      return reply;
    }
  }
  return FALLBACK;
}

window.SS = { PRODUCTS, SUGGESTIONS, findReply };
