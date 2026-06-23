# In-Progress Tasks
_Updated by all pipeline agents after each session._

## WOAW — WhatsApp Order Auto-Wrangler

### ✅ Completed
- **Frontend modularization**: extracted dashboard/login/order_card fragments, dynamic fragment loader with retry (3×, exponential backoff), event delegation for all fragment handlers, fallback UI
- **FastAPI backend scaffolding** (`orderstream/backend/`): complete, verified (app loads, 24 routes registered, syntax + import clean)
- **Mobile app (React + Vite + Tailwind)**: full auth flow, orders page, WhatsApp page, dashboard page; builds successfully (182KB JS)
- **WhatsApp webhook**: `POST /api/v1/webhooks/incoming` with `X-Webhook-Secret` shared secret auth; `webhooks.router` wired into `main.py`
- **JANUS deployment package**: Dockerfile, docker-compose.yml, nginx.conf, systemd unit, .env.production template; `GENERATED_UI_PATH` made configurable; backend verified loading cleanly
- **RAZE code audit — CRITICAL/HIGH fixes applied**:
  - Added `slowapi`, `prometheus-client` to requirements.txt; removed non-existent `baileys` package
  - Fixed `order_service.py` duplicate `update_order_status` and string pagination (now uses `Query.limit`/`Query.offset`)
  - Fixed `orders.py` inline import in `fulfill` — moved to module-level
  - Fixed `whatsapp.py` disconnect logic — now calls `set_disconnected` instead of `set_connected`
  - Added `set_disconnected` helper to `whatsapp_service.py`
  - Fixed `whatsapp/index.js` webhook URL (`/api/v1/webhooks/incoming`) and added `X-Webhook-Secret` header
  - Fixed `nginx.conf` invalid `proxy OPTIONS` directive
  - Fixed `dashboard_service.py` to include `confirmed` and `cancelled` in stats
  - Renamed `mobile/package.json` name `woaw-mobile` → `orderstream-mobile`
  - Updated `deploy/.env.production` paths/secrets from `waw` → `orderstream`
  - Removed `waw`/`WOAW` stale references from backend code and comments

### 🔜 Next
- **JANUS deploy** → push to `vmi3284252:/opt/overlord/orderstream/` using docker-compose
- Appwrite collections setup (`orders`, `users`) — needs Appwrite credentials + collection creation
- Baileys WhatsApp session management (QR code flow) — `services/whatsapp_service.py` and `routers/whatsapp.py` have stubs, need real implementation
- Payment integration (Paystack/M-Pesa) — `services/payments.py` stub, `routers/payments.py` raises 501

### 📅 Last Updated
2026-06-20
2026-06-20 SCRIBE | WOAW | COMPLETE | Gumroad copy ready