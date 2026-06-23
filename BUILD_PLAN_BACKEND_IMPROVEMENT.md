# Build Plan – Backend Improvements

## Overview
The backend (FastAPI) currently has hardcoded secrets, lacks health checks, rate limiting, structured logging, proper environment validation, and tests. This plan upgrades the backend to production readiness per the checklist.

## Tasks
- [ ] Refactor config to require all secrets via environment variables; remove hardcoded defaults.
- [ ] Add Pydantic Settings validation; abort startup if required vars missing.
- [ ] Secure JWT secret: enforce at least 256-bit length, read from env.
- [ ] Implement health endpoints (`/health`, `/ready`) with dependency checks (DB, cache).
- [ ] Add request logging middleware (JSON structured logs: timestamp, level, request_id, method, path, status, duration).
- [ ] Integrate Prometheus metrics (request count, latency, error rate) with `/metrics`.
- [ ] Apply rate limiting middleware (e.g., slowapi) with per‑user/IP limits, stricter on auth endpoints.
- [ ] Enforce CORS using origins from env, reject others.
- [ ] Implement API versioning (`/api/v1/...`) and update routers accordingly.
- [ ] Add pagination utilities to list endpoints, return cursor‑based pagination.
- [ ] Add standardized response models (status, data, error) using Pydantic BaseModel.
- [ ] Secure endpoints with RBAC: restrict export, payment, and admin routes.
- [ ] Add audit logging for sensitive actions (export, payment, order confirmation).
- [ ] Write unit/integration tests for critical paths (order export, auth, health).
- [ ] Set up CI pipeline (GitHub Actions) to run lint, tests, security scans, build Docker image.
- [ ] Create Dockerfile with multi‑stage build, pin exact dependency versions, expose only needed ports.
- [ ] Add systemd service file for production run, with auto‑restart and graceful shutdown handling.
- [ ] Add OpenAPI docs customization (title, version) and serve at `/docs` and `/redoc`.
- [ ] Update README with env var list, run instructions, deployment steps.
- [ ] Add backup script for database dump, scheduled via cron, with verification step.
- [ ] Implement graceful shutdown signal handling in FastAPI app (SIGTERM).
- [ ] Ensure all dependencies are pinned in `requirements.txt` and scanned for CVEs.

## Acceptance Criteria
- Application starts only when all required env vars are present.
- No secret values remain in source code.
- `/health` returns 200 when DB and cache are reachable; `/ready` similar.
- Structured logs appear in JSON format.
- Rate limiting returns 429 with `Retry-After`.
- Export endpoint passes integration test and produces correct CSV.
- CI pipeline passes on every push.
- Docker image builds without `latest` tags and runs with proper entrypoint.
- All new code is covered by tests achieving ≥80% coverage on critical modules.
