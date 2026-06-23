# Project Context

## Owner
Victory Phillips — OVERLORD Empire, AI services agency, Lagos

## Active Projects

### WhatsApp Order Auto-Wrangler (WOAW)
- **BUILD PLAN:** `BUILD_PLAN_WAWRANGLER.md`
- **Stage:** Frontend modularization complete; backend scaffolding in progress
- **Stack:** FastAPI + Appwrite + Capacitor React mobile app
- **Source:** SPECTRAL handoff (2026-06-17)
- **Files:** `orderstream/` directory — backend at `orderstream/backend/`, WhatsApp service at `orderstream/whatsapp/`

## Active Stack
- Backend: Python (FastAPI), Go (Gin), Rust (Axum), TypeScript (Hono)
- Frontend: Google Stitch → LOOM → VULCAN (react-components / shadcn / react-native)
- Deployment: Coolify on VPS via GitHub push
- VPS Python venv: /opt/overlord/venv/bin/python3

## Deployment Target
Coolify on VPS (vmi3284252). All services containerized.

## Key Files
- `generated_ui/index.html` — Merchant dashboard shell (2087 lines) with dynamic fragment loading
- `generated_ui/templates/dashboard.html` — Extracted dashboard fragment (data-action handlers)
- `templates/login.html` — Extracted login fragment
- `templates/order_card.html` — Extracted order card component
- `BUILD_PLAN_WAWRANGLER.md` — Full project specification
- `BUILD_PLAN_BACKEND_IMPROVEMENT.md` — Backend improvement plan