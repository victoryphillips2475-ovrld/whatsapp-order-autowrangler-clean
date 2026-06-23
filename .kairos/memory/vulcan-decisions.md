# VULCAN Architecture Decisions
_Decisions recorded here after each build session._

## 2026-06-19 — WOAW Frontend Modularization

### Fragment Directory Strategy
- **Decision:** Fragment directory is `generated_ui/templates/` (co-located with source)
- **Rationale:** Keeps templates alongside the main HTML, easier deployment
- **Exception:** Order card at project root `templates/` as a standalone component

### Event Delegation Pattern
- **Decision:** `data-action` attribute chosen over individual `addEventListener` per element
- **Implementation:** Single central delegation handler on `document` routes by `e.target.closest('[data-action]')`
- **Covered actions:** `open-order-drawer`, `toggle-row-action-menu`, `open-metric-modal`, form submits

### Fragment Loader
- **Retry:** Up to 3 attempts, exponential backoff (capped at 8s), writes `dataset.fragmentLoaded` to prevent double-fetch
- **Fallback:** Shows error UI with inline Retry and Reload buttons

### Inline Handler Migration
- **Decision:** All `onclick=` and `onsubmit=` attributes replaced with `data-action` + event delegation
- **Login form:** `document.addEventListener('submit')` filtering by `e.target.id === 'login-form'`
- **Confirm buttons:** `document.addEventListener('click')` using `e.target.closest('.confirm-btn')`

---

## 2026-06-19 — WOAW Backend FastAPI Scaffold

### Package Structure
- **Flat structure:** `orderstream/backend/` (not `orderstream/backend/app/`) — matches pre-existing scaffold
- **Package root:** `orderstream.backend` (import from parent of `orderstream/`)

### Router Prefixes
- **Pattern:** `main.py` sets the full prefix at `include_router` time; routers do NOT define their own `prefix=`
- **Why:** Double-prefix was causing `/api/v1/orders/orders/` instead of `/api/v1/orders/`

### Appwrite Integration
- **SDK pattern:** Synchronous Appwrite SDK wrapped in `run_in_threadpool` (thread pool size 4)
- **Collections:** `orders` (main) and `users` (auth) — Appwrite credentials needed in `.env`

### Auth
- **JWT:** `python-jose` with `HTTPBearer` + cookie fallback (cookie takes precedence over header)
- **Password hashing:** `passlib[bcrypt]` via `CryptContext`
- **Registration:** Stores in Appwrite `users` collection with bcrypt hash

### WhatsApp Stubs
- **QR generation:** Placeholder using `qrcode` lib (in-memory store keyed by `settings.WHATSAPP_SESSION_ID`)
- **Send message:** Stub in `whatsapp_service.py` that logs but doesn't send — needs Baileys or Cloud API

### Missing / Incomplete
- Baileys real session management (stub in place, not wired to Baileys SDK yet)
- Payment link generation (`routers/payments.py` raises 501)
- Appwrite `users` collection schema (needs creation)

---

## 2026-06-20 — WOAW Mobile App + WhatsApp Webhook

### Mobile Stack
- **Framework:** React 18 + Vite + TypeScript (Capacitor-ready)
- **Navigation:** `react-router-dom` v6 with `BrowserRouter`, `ProtectedRoute` wrapper
- **Styling:** Tailwind CSS v3 via PostCSS, `package.json` includes `"type": "module"` to suppress PostCSS CJS warning
- **API proxy:** `vite.config.ts` proxies `/api/v1` → `http://localhost:8000`; `VITE_API_URL` env var overrides in production
- **Auth persistence:** JWT stored in `localStorage` key `waw_jwt`; `ApiError` class with `.status` and `.detail`; auto-logout on 401 via `auth.tsx` refresh interceptor

### Mobile Pages
- `LoginPage` — phone + password, navigates to `/` on success
- `RegisterPage` — name + phone + password, auto-logs in after registration
- `OrdersPage` — real API calls, status filter, expandable rows, inline confirm/fulfill/payment-link, pagination
- `WhatsAppPage` — polls `GET /whatsapp/status` every 5s, base64 QR via `data:image/png;...`, disconnect button, auto-refresh
- `DashboardPage` — `GET /dashboard/stats`, flexible key-value cards with `LABEL_MAP`/`COLOR_MAP`

### WhatsApp Webhook Auth
- **Shared secret** (`X-Webhook-Secret` header) instead of JWT — Baileys Node service has no merchant JWT
- `WEBHOOK_SECRET` added to `config.py` settings with production guard (disallows dev default in non-dev env)
- `webhooks.router` mounted at `/api/v1/webhooks` (no JWT dependency — has its own `verify_webhook_secret` dependency)
- Route: `POST /api/v1/webhooks/incoming` — receives `{from, body, timestamp}` from Baileys Node, parses order, stores via `create_order`

### Backend Router Mounts (all under `/api/v1`)
- `/auth/*` — public (login, logout, me)
- `/orders/*` — JWT protected
- `/payments/*` — JWT protected
- `/whatsapp/*` — JWT protected
- `/dashboard/*` — JWT protected
- `/webhooks/*` — public (X-Webhook-Secret auth only)

### tsconfig.json Fixes
- Removed missing `@tsconfig/node16` extends
- Changed `moduleResolution` from `node` to `bundler` (Vite-compatible)
- Result: build succeeds (41 modules, 182KB JS, 14KB CSS)

---

## 2026-06-20 — WOAW JANUS Deployment Package

### Deployment Target
- **VPS:** `vmi3284252` at `/opt/overlord/orderstream/`
- **Topology:** nginx (port 80/443) → FastAPI backend (port 8000, no public exposure)
- **Static files:** `generated_ui/` and `mobile/dist/` mounted into nginx container as volumes

### Static Path Fix
- `main.py` hardcoded `/home/overlord/.openclaw/workspace/VULCAN/generated_ui` — replaced with `settings.GENERATED_UI_PATH` env var
- `GENERATED_UI_PATH` added to `config.py` with safe default; Docker sets it to `/app/generated_ui`, systemd uses host path

### Deployment Files (in `deploy/`)
| File | Purpose |
|---|---|
| `Dockerfile` | Single-stage Python 3.12 slim image, non-root user, healthcheck |
| `docker-compose.yml` | `backend` + `nginx` services, volume mounts for `generated_ui` + `mobile/dist` |
| `nginx.conf` | Reverse proxy routing `/api/v1/*` → backend, `/ui/*` + `/mobile/*` as static; CSP headers, rate limiting, gzip |
| `orderstream-backend.service` | Systemd unit for bare-metal deploy (no Docker); `overlord` user, WorkingDirectory=/opt/overlord/orderstream |
| `.env.production` | All env vars documented with REQUIRED flags and generation commands |

### Nginx Routing
- `/api/v1/*` → `upstream waw_backend` (keepalive 32), rate-limited (60 req/min global, 10 req/min auth)
- `/ui/*` → `alias /usr/share/nginx/html/ui/` with `try_files $uri $uri/ /ui/index.html` (SPA fallback)
- `/mobile/*` → `alias /usr/share/nginx/html/mobile/` with SPA fallback
- Relaxed CSP on `/mobile/*` for Capacitor (`'unsafe-eval'`)
- `/health` → synthetic 200 (no backend required for load balancer probes)

### Coolify Notes
- `docker-compose.yml` is the Coolify deployment entry point
- Bind `deploy/nginx.conf` → `/etc/nginx/nginx.conf` in nginx container
- Bind `generated_ui/` and `mobile/dist/` as volumes into nginx container

---

## 2026-06-20 — RAZE Audit Fixes (CRITICAL/HIGH)

### Dependency Fixes
- **Removed non-existent `baileys==6.1.2`** from requirements.txt — no such PyPI package
- **Added `slowapi==0.1.9`** — required by `main.py` rate limiter
- **Added `prometheus-client==0.19.0`** — required by `main.py` metrics endpoint
- `httpx` was already present; Dockerfile healthcheck will now work after requirements fix

### order_service.py
- **Removed duplicate `update_order_status`** — second copy (lines 246–263) was dead code
- **Fixed pagination** — changed `queries = [f"limit={limit}", f"offset={offset}"]` (raw strings) to `Query.limit(limit)` / `Query.offset(offset)` objects per Appwrite SDK v6 API

### orders.py router
- **Removed inline import** `from ..services.order_service import update_order_status` inside `fulfill()` — moved to module-level import alongside existing `list_orders`, `create_order`, etc.

### whatsapp.py router
- **Fixed disconnect logic** — was calling `set_connected()` instead of clearing session; now calls new `set_disconnected()` helper
- Added `set_disconnected` import from `whatsapp_service`

### whatsapp_service.py
- **Added `set_disconnected()` helper** — properly marks session as disconnected in `_STORE` dict

### whatsapp/index.js (Node.js)
- **Fixed webhook URL** — changed `/whatsapp/incoming` → `/api/v1/webhooks/incoming`
- **Added `X-Webhook-Secret` header** — reads from `process.env.WEBHOOK_SECRET`, sends as header

### nginx.conf
- **Removed invalid `proxy OPTIONS;`** directive — causes nginx parse failure; CORS preflight is handled by FastAPI's CORSMiddleware
- Updated "WAW" header comment → "OrderStream"

### dashboard_service.py
- **Added missing statuses** — now returns `pending`, `confirmed`, `completed`, `cancelled` (was only pending + completed)

### Stale Reference Cleanups
- `mobile/package.json`: `"name": "woaw-mobile"` → `"name": "orderstream-mobile"`
- `deploy/.env.production`: `WHATSAPP_SESSION_ID=waw_prod_session` → `orderstream_prod_session`; fixed `GENERATED_UI_PATH` from `/opt/overlord/waw/` → `/opt/overlord/orderstream/`; CORS example from `waw.yourdomain.com` → `orderstream.yourdomain.com`
- `orderstream/backend/create_appwrite_collections.py`: WOAW → OrderStream in docstring; removed unused `appwrite.id.ID` import