### PRODUCT NAME
WhatsApp Order Auto‑Wrangler

### TAGLINE
Turn messy WhatsApp order texts into structured orders without manual entry.

### DESCRIPTION
Micro‑retailers in Africa spend hours copying WhatsApp messages into spreadsheets, losing sales and making mistakes. The WhatsApp Order Auto‑Wrangler solves that by listening to incoming WhatsApp Business messages, extracting order details with a rule‑based parser, and storing them in a reliable Appwrite database.

The service provides a web‑based merchant dashboard to view, filter, confirm, and export orders, plus a Capacitor‑based mobile app that lets merchants scan a QR code to link their WhatsApp account, see incoming orders in real time, and mark them fulfilled.

Buy the zip file and get the complete backend (FastAPI), frontend (React + Capacitor), Docker‑Compose deployment scripts, Appwrite collection schemas, environment configuration template, and this README. You can have a running order‑automation system up in minutes on your own VPS.

This product is for tech‑savvy small business owners who can run Docker and manage a VPS. It is not for non‑technical users who need a fully managed SaaS solution.

### FEATURES
- WhatsApp order parsing via rule‑based regex (80% of common African SMB order formats).
- Baileys QR login for non‑Business WhatsApp accounts.
- Automatic order confirmation (currently logs, can be extended to real messages).
- Merchant dashboard with order list, status filters, and CSV export.
- Capacitor mobile app with QR scanner, order view, and fulfillment toggle.
- Docker‑Compose stack ready for Coolify deployment.
- Optional Paystack/M‑Pesa payment link generation (stubbed).

### WHAT YOU GET
- `orderstream/` directory with full backend and frontend source code.
- Dockerfile, docker‑compose.yml, and Nginx config for production.
- Appwrite collection JSON schemas.
- `.env.example` with all required environment variables.
- Detailed user documentation (`docs/README.md`).
- Deployment guide and setup instructions.

### PRICING NOTES
The product scope matches the BUILD PLAN MVP: core order parsing, QR login, dashboard, and mobile app. No optional payment integration or multi‑language support is included. Pricing should reflect a one‑time purchase for the codebase plus a modest fee for support.

### TAGS
whatsapp, order automation, micro‑retail, appwrite, fastapi, react, capacitor, docker, africa