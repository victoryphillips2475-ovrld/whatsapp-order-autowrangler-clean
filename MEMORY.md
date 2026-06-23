# VULCAN — LONG-TERM MEMORY

## Architecture Decisions
- Cron jobs are defined in `/home/overlord/.openclaw/cron/` and should be referenced to avoid forgetting.

## VPS Backend Structure — OrderStream
- **Package root:** `orderstream/` (import as `orderstream.backend`)
- **App run:** `cd orderstream && /opt/overlord/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
- **Static UI:** `app.mount("/ui", StaticFiles(directory="../../generated_ui", html=True))`
- **Pre-existing scaffold:** Production-grade structure already existed (security headers, rate limiting, Prometheus). VULCAN extended it by filling in missing router/model/service files.
- **Key files:** `orderstream/backend/main.py`, `orderstream/backend/config.py`, `orderstream/backend/dependencies.py`, `orderstream/backend/services/order_service.py`

## Lessons Learned
- Fragment loader must clear `dataset.fragmentLoaded` before retrying, else skip logic fires first and prevents re-fetch
- FastAPI router `prefix=` must NOT duplicate the prefix already set in `app.include_router(..., prefix=...)` — causes double-prefix routes like `/api/v1/orders/orders/`

## Active Projects
- **WhatsApp Order Auto-Wrangler (WOAW)** — `BUILD_PLAN_WAWRANGLER.md`
  - Frontend: `generated_ui/index.html` (modularized with dynamic fragment loading)
  - Backend: Not yet scaffolded — next VULCAN task
  - Target: African micro-retailers using WhatsApp Business for orders

## Kilo Code CLI via OpenClaw ACP
VULCAN can access Kilo Code CLI through OpenClaw's ACP system.
- **acpx plugin:** enabled in openclaw.json
- **Agent ID:** `kilocode`
- **Access method:** `sessions_spawn(runtime: "acp", agentId: "kilocode", ...)`
- **Direct CLI:** `npx -y @kilocode/cli acp` (via acpx)
- **ACP router skill:** `/home/overlord/.openclaw/plugin-skills/acp-router/SKILL.md`
- **Timeout:** 120 seconds (configured in openclaw.json)

## VULCAN Operational Directives

### Non-Negotiable Points (From Your Majesty)
1. **Baileys over WhatsApp Business API** — Users without WhatsApp Business should be able to connect via WA Web using Baileys (QR code scan). Include QR code screen in the app.
2. **Build Fast** — 4 weeks is the max ceiling, not a target. Finish in 5–6 hours if possible.
3. **User-Friendly Install** — No GitHub pulls, no Docker commands for end users. Users expect a website download or Play Store install. Design for non-technical users.
4. **Self-Hosted Stack** — App connects to the VPS (same host as Coolify and the database). Appwrite is on the VPS.
5. **VULCAN is the Overseer** — Delegate to sub-agents, don't do all the work yourself.

### Sub-Agent Roster (in /home/overlord/.openclaw/workspace/VULCAN/agents/)
| Agent | Role |
|---|---|
| BLUEPRINT | Builds the detailed SPEC + BUILD PLAN from a SPECTRAL brief. VULCAN reads it, then spawns coding agents. |
| LOOM | Frontend architect. Designs UI, delivers design.md with APPROVED FOR BUILD. |
| CODEX | Legal docs (ToS, Privacy Policy, etc.) |
| ALCHEMIST | Pre-build dependency audit gate |
| RAZE | Post-build code critic |
| MORPH | Post-RAZE cleanup of MEDIUM/BLOAT issues |
| WEAVE | Frontend-backend integration verifier |
| SENTINEL | Security audit + penetration testing |
| JANUS | GitHub → Coolify → startup verification |
| SCRIBE | Product.md finalisation + Gumroad listing copy |

### Pipeline Order
BLUEPRINT → LOOM → VULCAN → CODEX → LOOM → ALCHEMIST → RAZE → MORPH → WEAVE → SENTINEL → JANUS → SCRIBE

### Handoff Naming Convention
Files in `/home/overlord/.openclaw/shared/` must follow: `{SOURCE_AGENT}-{TARGET_AGENT}-Handoff-{YYYY-MM-DD}.md`

## Promoted From Short-Term Memory (2026-06-22)

<!-- openclaw-memory-promotion:memory:memory/2026-06-18.md:29:29 -->
- VULCAN Heartbeat Handoff Summary - 2026-06-18: **Competitive Edge:** $29‑$79/mo pricing (Basic/Pro/Enterprise), built‑in local payment gateways, simplicity vs. expensive generic tools (Zapier, Zoko). [score=0.857 recalls=0 avg=0.620 source=memory/2026-06-18.md:29-29]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19.md:3:3 -->
- VULCAN Heartbeat Handoff - 2026-06-19 05:55 AM CEST: Processed handoff file: SPECTRAL-VULCAN-Handoff-2026-06-17.md [score=0.857 recalls=0 avg=0.620 source=memory/2026-06-19.md:3-3]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19.md:5:5 -->
- VULCAN Heartbeat Handoff - 2026-06-19 05:55 AM CEST: Summary: Handoff from SPECTRAL regarding WhatsApp Order Auto‑Wrangler (Pain Point #1). Targets African micro‑retailers using WhatsApp Business for orders, suffering manual entry into Excel/Tally. Proposed solution: AI‑light parser to extract orders from WhatsApp, store in Appwrite, send confirmations, optional payment links (Paystack/M‑Pesa), dashboard, CSV export. Success metrics: ≥80% time saved, ≤1% error rate. Pricing: $29‑$79/mo. Viability score: 24/30 (weighted ~66.7). Priority: HIGH. Next action: Begin detailed design & development of MVP (4‑week sprint). [score=0.857 recalls=0 avg=0.620 source=memory/2026-06-19.md:5-5]

## Promoted From Short-Term Memory (2026-06-23)

<!-- openclaw-memory-promotion:memory:memory/2026-06-18.md:7:7 -->
- VULCAN Heartbeat Handoff Summary - 2026-06-18: **Problem:** Small CPG/food brands and micro‑retailers in Africa (Nigeria, Kenya, Ghana) manually copy‑paste WhatsApp Business orders into Excel or Tally, wasting hours daily and introducing transcription errors. [score=0.893 recalls=0 avg=0.620 source=memory/2026-06-18.md:7-7]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18.md:16:16 -->
- VULCAN Heartbeat Handoff Summary - 2026-06-18: **Core Features:** [score=0.893 recalls=0 avg=0.620 source=memory/2026-06-18.md:16-16]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18.md:26:27 -->
- VULCAN Heartbeat Handoff Summary - 2026-06-18: **Flow A:** WhatsApp message → Parse → Store → Confirmation → Dashboard; **Flow B:** Order stored → Merchant enables payment → System sends Paystack/M‑Pesa link → Customer pays → Order status updated to Paid [score=0.893 recalls=0 avg=0.620 source=memory/2026-06-18.md:26-27]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18.md:3:5 -->
- VULCAN Heartbeat Handoff Summary - 2026-06-18: **Source:** SPECTRAL **Handoff File:** SPECTRAL-VULCAN-Handoff-2026-06-17.md **Product:** WhatsApp Order Auto‑Wrangler [score=0.861 recalls=0 avg=0.620 source=memory/2026-06-18.md:3-5]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18.md:9:9 -->
- VULCAN Heartbeat Handoff Summary - 2026-06-18: **Target User:** Owner/Operations Manager of micro‑retail food‑delivery or CPG distributors (1‑10 employees, <$500k annual revenue) in English‑speaking/Swahili African markets. [score=0.861 recalls=0 avg=0.620 source=memory/2026-06-18.md:9-9]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18.md:11:11 -->
- VULCAN Heartbeat Handoff Summary - 2026-06-18: **Success Metrics:** [score=0.861 recalls=0 avg=0.620 source=memory/2026-06-18.md:11-11]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18.md:12:14 -->
- VULCAN Heartbeat Handoff Summary - 2026-06-18: ≥80% reduction in manual order‑entry time (2 hrs/day → <15 min); ≤1% order transcription error rate (vs ~5% manually); Ability to process 2× more orders per day [score=0.861 recalls=0 avg=0.620 source=memory/2026-06-18.md:12-14]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18.md:17:20 -->
- VULCAN Heartbeat Handoff Summary - 2026-06-18: WhatsApp Cloud API/Twilio WhatsApp integration for inbound messages; Rule‑based parser (keywords, emojis) to extract product, quantity, price; Appwrite collection storage with timestamps and customer metadata; Automated order acknowledgement (text + optional Paystack/M‑Pesa payment link) [score=0.861 recalls=0 avg=0.620 source=memory/2026-06-18.md:17-20]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18.md:21:23 -->
- VULCAN Heartbeat Handoff Summary - 2026-06-18: CSV/Excel export on demand; Dashboard view of pending orders with status filtering; Optional Paystack (Nigeria) / M‑Pesa (Kenya) integration for one‑click payments [score=0.861 recalls=0 avg=0.620 source=memory/2026-06-18.md:21-23]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18.md:31:31 -->
- VULCAN Heartbeat Handoff Summary - 2026-06-18: **Viability Score:** 24/30 (weighted ~66.7) → Go‑ahead recommended. [score=0.861 recalls=0 avg=0.620 source=memory/2026-06-18.md:31-31]
