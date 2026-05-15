---
name: shopsmart-bd-design
description: Use this skill to generate well-branded interfaces and assets for ShopSmart BD — a fictional Bangladeshi e-commerce store whose support chatbot ("Shira") runs as a Streamlit + LangChain RAG app. Contains essential design guidelines, colors, type, fonts, assets, and a chatbot UI kit for prototyping production code or throwaway mocks.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

## What's in this skill

- `README.md` — full brand reference: product context, content fundamentals, visual foundations, iconography
- `colors_and_type.css` — design tokens (CSS variables) — drop into any HTML and you have the brand
- `assets/` — logo, mark, Shira avatar, payment icons, illustrations, photo placeholders
- `preview/` — per-token preview cards (open any of them to inspect a single concept)
- `ui_kits/chatbot/` — high-fidelity, mobile-friendly recreation of the Shira chat experience (React, JSX, no build step)

## Quickstart cheatsheet

- **Primary brand action:** `--brand-red` `#E63946`
- **Background canvas:** `--bg-canvas` `#FBF8F3` (warm paper — never pure gray)
- **Display face:** Manrope 800 (Google Fonts, loaded by `colors_and_type.css`)
- **Body face:** Source Sans 3 (Streamlit-native)
- **Currency:** `BDT 1,000` style — no decimals, no cents
- **Persona:** "Shira" — warm, professional, ≤ 3 sentences, never fabricates, always cites
- **Emoji:** only 🛍️ in browser-tab favicon position; none inside product UI
- **Icons:** Lucide, stroke 1.75, currentColor

## Source of truth

This skill was derived from https://github.com/auntor101/Smartshop-RAG-ChatBot — the upstream Streamlit RAG application. If anything here drifts from that repo, treat the repo as authoritative and revise.
