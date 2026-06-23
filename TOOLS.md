# Tools — VULCAN

## Primary LLM — NIM (NVIDIA)
All reasoning runs through NIM free-tier models on https://integrate.api.nvidia.com/v1.

- **minimaxai/minimax-m2.7** — Primary model (200K context, 230B MoE, agentic coding)
- **meta/llama-3.3-70b-instruct** — Fallback for general reasoning (131K context)
- **meta/llama-3.1-8b-instruct** — Fast routing and simple lookups (131K context)

## Code Execution Environment
- Python venv: /opt/overlord/venv/bin/python3
- Bash: Available via tool calls
- VPS working directory: /home/overlord/
- Code-server: localhost:8080 (behind nginx on VPS)

## API Keys

| Service | Key | Env Var |
|---|---|---|
| Tavily | tvly-YOUR_KEY_HERE | TAVILY_API_KEY |
| Firecrawl | fc-YOUR_KEY_HERE | FIRECRAWL_API_KEY |

Replace the placeholder values above with your actual keys.

## Web Search — Tavily + Firecrawl (Primary)
- **Tavily:** Default for search queries. API key from env: `TAVILY_API_KEY`
- **Firecrawl:** Default for full page extraction and scraping. API key from env: `FIRECRAWL_API_KEY`

## Web Search — SearXNG (Fallback Only)
Self-hosted at http://localhost:8888. Use only when Tavily/Firecrawl are unavailable or rate-limited. NEVER port 8080.

## Workflow Automation — n8n
Webhook base: http://localhost:5678.

## KAIROS Tech Stack Reference — FORGE Picks

### API Frameworks
- **FastAPI** — Primary Python API (FORGE pick)
- **Hono** — Edge-first TypeScript, Cloudflare Workers compatible (FORGE pick)
- **Gin** — Go framework when throughput matters (FORGE pick)

### BaaS
- **Appwrite** — Primary BaaS: DB, Auth, Storage, Realtime (FORGE pick)
- **PocketBase** — Single binary alternative for lightweight deployments (FORGE pick)

### Databases
- **PostgreSQL** — Primary relational DB, pgvector for AI embeddings (FORGE pick)
- **Redis** — Cache, pub/sub, session store, message queue (FORGE pick)

### ORM
- **SQLAlchemy** — Python ORM standard (FORGE pick)

### Auth
- **Clerk** — Pre-built UI, org management, passkeys (FORGE pick)
- **Better Auth** — Open source TypeScript alternative (FORGE pick)

### Deployment
- **Coolify** — Self-hosted on VPS, primary deployment (FORGE pick)
- **Railway** — Managed fallback, fastest DX (FORGE pick)

### Background Jobs
- **Celery + Redis** — Python distributed task queue, empire standard (FORGE pick)

### Storage
- **MinIO** — Self-hosted S3-compatible on VPS (FORGE pick)

### Real-time & WebSockets
- **Soketi** — Self-hosted Pusher-compatible WebSocket server (FORGE pick)

### Reverse Proxy
- **Traefik** — Docker-native, auto-discovers services, auto SSL (FORGE pick)

### Monitoring
- **Grafana + Prometheus** — Metrics, dashboards, alerting (FORGE pick)
- **Sentry** — Error tracking, self-hostable on VPS (FORGE pick)

### Mobile Bridge
- **Capacitor** — Wraps web output into iOS/Android native shell
- **Expo** — React Native, EAS Build for App Store/Play Store

## Memory System
- SQLite: Structured memory backbone
- Mem0: Cross-session relational memory per entity
- Daily logs: memory/YYYY-MM-DD.md
- Long-term: MEMORY.md

## Communication Channels
- Telegram: @Overlordempirezcontact_bot (receives task routing)
- WhatsApp: +18257898450 (outreach only — VULCAN does not write outreach)

## Key Infrastructure
- Appwrite: Primary database (SDK, not raw HTTP)
- Coolify: Deployment platform on VPS
- n8n: Workflow and webhook orchestration
- Brevo: Email gateway
- FFmpeg: /usr/bin/ffmpeg

## KAIROS Pipeline Paths
- Pipeline root: /home/overlord/.openclaw/
- SCOUT: /home/overlord/.openclaw/workspace/SCOUT/kairos_scout_v2/
- Pipeline order: SCOUT → HOOK → QUALIFIER → HANDLER → ARCHITECT → CLOSER+PRICING → CIPHER → PHANTOM → RETAINER

## OpenClaw
- Config: /home/overlord/.openclaw/openclaw.json
- Workspace root: /home/overlord/.openclaw/workspace/
- VULCAN workspace: /home/overlord/.openclaw/workspace/VULCAN/
