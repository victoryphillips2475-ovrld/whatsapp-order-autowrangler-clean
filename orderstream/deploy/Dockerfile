# FILE: /home/overlord/.openclaw/workspace/VULCAN/deploy/Dockerfile
# ─────────────────────────────────────────────────────────────────────────────
# OrderStream Backend — single-stage production image
# ─────────────────────────────────────────────────────────────────────────────
# Build:  docker build -t orderstream-backend:latest -f deploy/Dockerfile .
# Run:    docker run --env-file deploy/.env.production orderstream-backend:latest
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

# Security: run as non-root user
RUN groupadd -r orderstream && useradd -r -g orderstream orderstream

WORKDIR /app

# Install dependencies first (better layer cache)
COPY orderstream/backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Copy source (exclude tests, docs, IDE files)
COPY orderstream/backend/ .

# Recreate venv with only installed packages for smaller attack surface
FROM python:3.12-slim
RUN groupadd -r orderstream && useradd -r -g orderstream orderstream
WORKDIR /app

# Copy installed packages from builder
COPY --from=0 /install /usr/local

# Copy source (must include the StaticFiles dir mount at runtime via env)
COPY --chown=orderstream:orderstream orderstream/backend/ .

# Drop privileges
USER orderstream

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Expose port
EXPOSE 8000

# Run via uvicorn — workers=1 for simplicity; use gunicorn for multi-worker
CMD ["uvicorn", "orderstream.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]