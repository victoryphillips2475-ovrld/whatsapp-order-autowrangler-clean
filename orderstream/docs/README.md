# WhatsApp Order Auto‑Wrangler

WhatsApp Order Auto‑Wrangler automates order intake for African micro‑retailers by turning WhatsApp messages into structured orders stored in Appwrite. It provides a web dashboard and a Capacitor React mobile app for merchants to view, confirm, fulfill, and export orders.

## Getting Started
- Clone the repository: `git clone <repo_url>`
- Copy the example environment file: `cp orderstream/backend/.env.example orderstream/backend/.env`
- Fill in all required variables in `.env` (see Environment Variables table below).
- Build and start the services with Docker Compose: `docker compose up -d`
- The backend API will be available at `http://localhost:8000/api/v1`.
- Access the merchant dashboard at `http://localhost:8000/dashboard.html` (served by Nginx).
- Install the mobile app dependencies: `cd mobile && npm install`
- Run the mobile app in a simulator or on a device: `npm run ios` or `npm run android` (Capacitor).

## Environment Variables
| Variable | Purpose | Example |
|---|---|---|
| APP_ENV | Runtime mode (`production`/`development`). | production |
| APP_HOST | Host binding for FastAPI. | 0.0.0.0 |
| APP_PORT | Port FastAPI listens on. | 8000 |
| CORS_ORIGINS | Allowed origins for browser apps. | https://orderstream.yourdomain.com |
| JWT_SECRET | Base64‑encoded secret for signing JWTs. | change_me_before_production_min_44_base64_chars |
| JWT_ALGORITHM | JWT algorithm (`HS256`). | HS256 |
| JWT_EXPIRE_MINUTES | Token TTL. | 60 |
| APPWRITE_ENDPOINT | Appwrite API base URL. | https://cloud.appwrite.io/v1 |
| APPWRITE_PROJECT_ID | Appwrite project identifier. | your_project_id_here |
| APPWRITE_API_KEY | Server‑side API key (keep secret). | your_server_api_key_here |
| APPWRITE_DATABASE_ID | Database containing `users` and `orders`. | your_database_id_here |
| WEBHOOK_SECRET | Shared secret for authenticating Baileys webhook requests. | change_me_to_a_32_byte_hex_secret |
| WEBHOOK_DEFAULT_USER_ID | Appwrite user ID assigned to orders created via webhook. | your_appwrite_user_id_here |
| WHATSAPP_PHONE | WhatsApp Business phone number (E.164). | +2340000000000 |
| WHATSAPP_SESSION_ID | Identifier for persisting Baileys session state. | orderstream_prod_session |
| ADMIN_USERNAME / ADMIN_PASSWORD | Initial admin credentials for the dashboard. | admin / change_this_password_before_production |
| PAYSTACK_SECRET_KEY | (Optional) Paystack secret for NGN payments. | sk_live_… |
| MPESA_CONSUMER_KEY / MPESA_CONSUMER_SECRET | (Optional) M‑Pesa credentials for KE payments. | your_key / your_secret |

## API Reference
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | /whatsapp/connect | Start Baileys session, returns QR code. | No |
| GET | /whatsapp/status | Get Baileys session status. | No |
| GET | /orders/ | List all orders. | Yes |
| POST | /orders/ | Create a manual order from message. | Yes |
| GET | /orders/{id} | Retrieve a single order. | Yes |
| POST | /orders/{id}/confirm | Send confirmation message to customer. | Yes |
| GET | /orders/export | Export orders as CSV file. | Yes |
| POST | /payments/link | Generate Paystack/M‑Pesa payment link. | Yes |
| GET | /dashboard/stats | Get order statistics (pending, completed). | Yes |

## Features
- WhatsApp order parsing with rule‑based extraction.
- QR code login for Baileys WhatsApp session.
- Automatic order confirmation via WhatsApp.
- Merchant dashboard with CSV export and status filters.
- Capacitor React mobile app with QR scanner for session connection.
- JWT authentication for all protected endpoints.
- Prometheus metrics and health/readiness probes.
- Docker‑Compose deployment with Nginx reverse proxy.

## Known Limitations
- Confirmation messages are currently logged only; no real WhatsApp message is sent.
- No automated test coverage yet; CI runs only lint checks.
- Health check validates only Appwrite connectivity; other services are not probed.
- Payment integration is optional and not included in the MVP.
- Monitoring and alerting are not configured.

## Support
Contact Victory Phillips, KAIROS Empire.
