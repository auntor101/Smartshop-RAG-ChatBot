# ShopSmart BD — Chatbot UI Kit

A high-fidelity recreation of the **Shira** customer support chat experience.
Modern, attractive, mobile-friendly. Built as a click-thru prototype with
canned responses so flows are deterministic and demo-able offline.

## Surfaces covered

- Header with brand mark + Shira identity + live status
- Welcome / empty state with brand hero and suggested questions
- Message thread (user + assistant bubbles + typing indicator)
- Inline **product card** answers (catalog from `data/shopsmart_docs/products.txt`)
- Inline **payment chip row** answers (bKash, Nagad, Visa, MC, PayPal, COD)
- Inline **delivery info** answer with illustration
- Expandable **source citations** under each Shira reply (RAG-grounded)
- Composer with auto-grow textarea, suggestion chips, send button
- Floating "scroll to bottom" pill when scrolled up

## Files

| File | Purpose |
|---|---|
| `index.html` | Mount + demo wiring (single-page, mobile-friendly) |
| `App.jsx` | Root state + message routing |
| `Header.jsx` | Sticky chat header |
| `Welcome.jsx` | Hero empty-state with suggestion chips |
| `Thread.jsx` | Scroll container + auto-scroll |
| `Message.jsx` | Assistant / user / system bubble + sources |
| `Composer.jsx` | Textarea + send button |
| `ProductCard.jsx` | Inline product card from catalog |
| `PaymentRow.jsx` | Inline payment-method chip row |
| `DeliveryCard.jsx` | Inline delivery summary |
| `Icons.jsx` | Lucide-style inline SVG icons |
| `responses.js` | Canned responses keyed by intent |

## Out of scope

- Real LLM round-trip (use `responses.js` keyword routing)
- Authentication, real cart, real orders
- Admin sidebar (the upstream Streamlit app has one — irrelevant for a customer-facing prototype)

## How to verify

Open `index.html` directly. The page is mobile-responsive — drag the preview narrow to see the phone layout (no separate "mobile" file needed).
