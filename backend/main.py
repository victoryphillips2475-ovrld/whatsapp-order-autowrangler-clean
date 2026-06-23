# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/main.py
"""FastAPI entry point for the WhatsApp Order Auto‑Wrangler backend."""

import uuid
import time
import logging
from datetime import datetime
from typing import List

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles

from slowapi.errors import RateLimitExceeded

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from .config import settings
from .limiter import limiter
from .routers import whatsapp, orders, payments, dashboard, auth, webhooks
from .dependencies import get_current_user  # used for auth on protected routes

# ---------------------------------------------------------------------------
# Global objects
# ---------------------------------------------------------------------------
app = FastAPI(
    title="WhatsApp Order Auto‑Wrangler API",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
)
app.state.limiter = limiter
# Serve static UI files (merchant dashboard). Path is configurable via
# settings.GENERATED_UI_PATH so Docker can inject the correct volume mount.
app.mount(
    "/ui",
    StaticFiles(directory=settings.GENERATED_UI_PATH, html=True),
    name="ui",
)

# ---------------------------------------------------------------------------
# Middleware – CORS, security headers, logging, rate‑limit handling
# ---------------------------------------------------------------------------
# CORS – origins are read from the env var; empty string means no access.
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enforce HTTPS in production – only when NOT behind a reverse proxy that
# terminates TLS (nginx does this for us, so we skip the middleware).
# If you run FastAPI directly on the internet, set APP_ENV=production and
# ENABLE_TLS_REDIRECT=true to activate the redirect.

# Structured request logging – JSON lines written to the ``uvicorn.access`` logger.
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(duration_ms, 2),
        "client_ip": request.client.host if request.client else "unknown",
    }
    logging.getLogger("uvicorn.access").info(log_entry)
    # Propagate the request ID downstream (useful for tracing).
    response.headers["X-Request-ID"] = request_id
    return response

# Security‑header middleware (static values – CSP could be refined later).
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; img-src 'self' data:; font-src https://fonts.gstatic.com https://fonts.googleapis.com;"
    response.headers["Server"] = "nginx"
    return response

# Rate‑limit exception handling – returns a JSON payload with ``Retry‑After``.
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded", "retry_after": exc.retry_after},
        headers={"Retry-After": str(exc.retry_after)},
    )

# ---------------------------------------------------------------------------
# Health & readiness probes
# ---------------------------------------------------------------------------
@app.get("/health")
async def health() -> dict:
    """Liveness probe – simple 200 when the process is running."""
    return {"status": "healthy"}

@app.get("/ready")
async def readiness() -> dict:
    """Readiness probe – verifies external dependencies.

    Currently checks that the Appwrite client can perform a cheap request
    (list collections). If the check fails the endpoint returns **503**.
    """
    from .services.order_service import _verify_appwrite_connection

    ready = await _verify_appwrite_connection()
    if not ready:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Appwrite not reachable")
    return {"status": "ready"}

# Prometheus metrics endpoint — requires authentication.
@app.get("/metrics")
async def metrics(_user: dict = Depends(get_current_user)) -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ---------------------------------------------------------------------------
# Router registration – protected routes require authentication via the ``get_current_user``
# dependency defined in ``dependencies.py``.
# ---------------------------------------------------------------------------
app.include_router(
    whatsapp.router,
    prefix="/api/v1/whatsapp",
    tags=["WhatsApp"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    orders.router,
    prefix="/api/v1/orders",
    tags=["Orders"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    payments.router,
    prefix="/api/v1/payments",
    tags=["Payments"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    dashboard.router,
    prefix="/api/v1/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Auth"],  # Auth router now under /api/v1 prefix – matches frontend base URL
)
app.include_router(
    webhooks.router,
    prefix="/api/v1/webhooks",
    tags=["Webhooks"],  # Webhooks have their own X-Webhook-Secret auth, no JWT needed
)

# Root endpoint – minimal information, no secrets.
@app.get("/")
async def root() -> dict:
    return {"message": "WhatsApp Order Auto‑Wrangler API is running"}

# ---------------------------------------------------------------------------
# Startup / shutdown – verify external services once at launch.
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def on_startup():
    # Attempt a quick health‑check against Appwrite; failures are logged.
    from .services.order_service import _verify_appwrite_connection

    if not await _verify_appwrite_connection():
        logging.getLogger("uvicorn.error").error("Appwrite connection failed during startup – service will be marked not ready")

@app.on_event("shutdown")
async def on_shutdown():
    logging.getLogger("uvicorn.error").info("Shutting down WhatsApp Order Auto‑Wrangler API")
