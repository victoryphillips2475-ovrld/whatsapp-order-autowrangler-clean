# WhatsApp Order Auto‑Wrangler
A SaaS service that lets African micro‑retailers receive orders via WhatsApp Business, automatically parses them, stores them in Appwrite, and provides a merchant dashboard and mobile app to manage orders.

## Getting Started
1. Install Docker and Docker‑Compose.
2. Clone the repository:
   git clone https://github.com/overlord/woaw.git
   cd woaw
3. Copy the example environment file and edit values:
   cp .env.example .env
   # Edit .env – set Appwrite credentials, JWT secret, webhook secret, etc.
4. Start the stack:
   docker-compose up -d
5. Verify the service is healthy:
   curl http://localhost:8000/health
6. Open the merchant dashboard in a browser:
   http://localhost:8080
7. For the mobile app, run the Capacitor build:
   cd mobile
   npm install
   npm run build
   npx cap add android   # or ios
   npx cap open android   # open Android Studio to build APK
8. Follow the QR code flow in the app to connect a WhatsApp account via Baileys.

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
| WEBHOOK_DEFAULT_USER_ID | Appwrite user ID for webhook‑created orders. | your_appwrite_user_id_here |
| WHATSAPP_PHONE | WhatsApp Business phone number (E.164). | +2340000000000 |
| WHATSAPP_SESSION_ID | Identifier for persisting Baileys session state. | orderstream_prod_session |
| ADMIN_USERNAME / ADMIN_PASSWORD | Initial admin credentials for the dashboard. | admin / change_this_password_before_production |
| PAYSTACK_SECRET_KEY | (Optional) Paystack secret for NGN payments. | sk_live_… |
| MPESA_CONSUMER_KEY / MPESA_CONSUMER_SECRET | (Optional) M‑Pesa credentials for KE payments. | your_key / your_secret |

## API Reference
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | /api/v1/orders/ | List all orders (paginated). | Yes |
| POST | /api/v1/orders/ | Create a manual order. | Yes |
| GET | /api/v1/orders/{id} | Retrieve a single order. | Yes |
| POST | /api/v1/orders/{id}/confirm | Send confirmation to customer (currently logs). | Yes |
| GET | /api/v1/orders/export | Export orders as CSV. | Yes |
| POST | /api/v1/payments/link | Generate Paystack/M‑Pesa payment link (optional). | Yes |
| GET | /api/v1/dashboard/stats | Get order statistics for dashboard. | Yes |

## Features
- WhatsApp order parsing using rule‑based regex.
- Baileys QR login for non‑Business WhatsApp accounts.
- Automatic order confirmation (currently logs, real send to be added).
- Merchant dashboard with order list, status filters, and CSV export.
- Capacitor mobile app with QR scanner, order view, and fulfillment toggle.

## Known Limitations
- Confirmation messages are logged only; no actual WhatsApp message is sent.
- No automated test suite – CI runs only lint.
- Health probe checks only Appwrite connectivity.
- Payment link generation is optional and not yet integrated.

## Support
Victory Phillips – contact@overlord.ai