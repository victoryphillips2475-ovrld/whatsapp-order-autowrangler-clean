# FILE: /home/overlord/.openclaw/workspace/VULCAN/deploy/orderstream-whatsapp.dockerfile
# ─────────────────────────────────────────────────────────────────────────────
# WhatsApp Baileys Node.js service
# ─────────────────────────────────────────────────────────────────────────────

FROM node:22-slim

WORKDIR /app

# Copy dependency manifest first (layer cache friendly)
COPY orderstream/whatsapp/package.json /app/package.json
COPY orderstream/whatsapp/package-lock.json* /app/package-lock.json 2>/dev/null || true

# Install dependencies
RUN npm ci --ignore-scripts 2>/dev/null || npm install --ignore-scripts

# Copy source
COPY orderstream/whatsapp/ /app/

# Environment — defaults for dev, override via docker-compose environment block
ENV NODE_ENV=production
ENV FASTAPI_URL=http://orderstream-backend:8000
ENV WEBHOOK_SECRET=whatsapp_webhook_secret_dev

# Session directory for Baileys auth state (persisted as Docker volume)
RUN mkdir -p /app/session && chown node:node /app/session

USER node

# Healthcheck: verify node process is alive
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD pgrep -x node > /dev/null || exit 1

EXPOSE 3000

CMD ["node", "index.js"]