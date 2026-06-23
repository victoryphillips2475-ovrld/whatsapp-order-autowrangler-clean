# WhatsApp Order Auto-Wrangler — BUILD PLAN

**Product:** WhatsApp Order Auto-Wrangler (WOAW)
**Source:** SPECTRAL handoff
**Priority:** HIGH
**Build Time Estimate:** 5–6 hours (MVP)

---

## 1. STACK

### Backend
- **Language:** Python 3.11
- **Framework:** FastAPI (patterns/fastapi.md)
- **Database:** Appwrite (self-hosted at 100.87.228.1)
- **WhatsApp Integration:** Baileys (WA Web) + WhatsApp Cloud API (fallback)
- **Payment Gateways:** Paystack (Nigeria), M-Pesa (Kenya) — optional
- **Task Queue:** Appwrite Functions
- **Parser:** Rule-based + regex (no heavy ML)

### Frontend
- **Mobile App:** Capacitor (React) + Tailwind CSS
- **Merchant Dashboard:** React + Tailwind CSS
- **QR Code Scanner:** `@capacitor-community/barcode-scanner`

### DevOps
- **VPS:** Same host as Coolify (100.87.228.1)
- **CI/CD:** GitHub Actions (patterns/app-store-deployment.md)
- **Deployment:** Docker (FastAPI) + Capacitor (Android APK)
- **Cloud Build:** EAS (Expo Application Services)

### Key Dependencies
```
# Backend
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0
pydantic-settings==2.6.0
httpx==0.27.0
python-dotenv==1.0.1
appwrite==6.0.0
python-jose[cryptography]==3.3.0
passlib==1.7.4
qrcode==7.4.2

# Frontend
react==18.3.1
react-dom==18.3.1
tailwindcss==3.4.1
@capacitor/core==6.1.0
@capacitor/android==6.1.0
@capacitor-community/barcode-scanner==5.0.0
```

---

## 2. FILE STRUCTURE
```
orderstream/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point + lifespan
│   │   ├── config.py               # Pydantic settings
│   │   ├── dependencies.py         # FastAPI Depends() functions
│   │   ├── models/
│   │   │   ├── orders.py             # Pydantic request/response models
│   │   │   ├── users.py              # User models
│   │   │   └── payments.py          # Payment models
│   │   ├── routers/
│   │   │   ├── orders.py            # Order endpoints
│   │   │   ├── whatsapp.py          # WhatsApp/Baileys endpoints
│   │   │   ├── payments.py          # Payment endpoints
│   │   │   ├── auth.py              # Auth endpoints
│   │   │   ├── dashboard.py         # Merchant dashboard endpoints
│   │   │   └── webhooks.py          # Inbound WhatsApp webhook
│   │   │   ├── services/
│   │   │   ├── orders.py            # Order business logic
│   │   │   ├── whatsapp.py          # WhatsApp/Baileys logic
│   │   │   ├── parser.py            # Order message parser
│   │   │   └── payments.py          # Payment logic
│   │   └── utils/
│   │       ├── auth.py            # JWT/auth utilities
│   │       └── qr.py              # QR code generator
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── mobile/
│   │   ├── src/
│   │   │   ├── App.tsx              # Main app entry
│   │   │   ├── pages/
│   │   │   │   ├── ScanQR.tsx         # Baileys QR scanner
│   │   │   │   ├── Orders.tsx        # Order list
│   │   │   │   └── Settings.tsx      # App settings
│   │   │   ├── components/
│   │   │   │   ├── OrderCard.tsx     # Order UI component
│   │   │   │   └── PaymentButton.tsx # Paystack/M-Pesa button
│   │   │   └── utils/
│   │   │       └── api.ts          # API client
│   │   ├── capacitor.config.ts     # Capacitor config
│   │   ├── tailwind.config.js
│   │   └── package.json
│   │
│   └── dashboard/
│       ├── src/
│       │   ├── App.tsx
│       │   ├── pages/
│       │   │   ├── Orders.tsx        # Order dashboard
│       │   │   └── Export.tsx       # CSV export
│       │   └── components/
│       │       ├── OrderTable.tsx  # Data grid
│       │       └── Sidebar.tsx     # Navigation
│       ├── tailwind.config.js
│       └── package.json
│
├── infra/
│   ├── appwrite/
│   │   ├── collections/
│   │   │   ├── orders.json         # Collection schema
│   │   │   └── users.json         # User schema
│   │   └── functions/
│   │       └── whatsapp-parser.json # Appwrite Function
│   └── docker-compose.yml        # Appwrite + FastAPI
│
└── .github/
    └── workflows/
        ├── backend.yml            # FastAPI CI/CD
        └── mobile.yml            # Capacitor/EAS build
```

---

## 3. API SCHEMA

### Base URL
`http://100.87.228.1:8000/api/v1`

### Endpoints

#### WhatsApp/Baileys
| Endpoint               | Method | Request Body                     | Response               | Description                          |
|------------------------|--------|----------------------------------|------------------------|--------------------------------------|
| `/whatsapp/connect`    | POST   | `{ "phone": "string" }`       | `{ "qr": "base64" }` | Start Baileys session, return QR    |
| `/whatsapp/status`     | GET    | -                                | `{ "status": "string" }` | Check session status               |

#### Orders
| Endpoint               | Method | Request Body                     | Response               | Description                          |
|------------------------|--------|----------------------------------|------------------------|--------------------------------------|
| `/orders/`             | GET    | -                                | `[OrderResponse]`      | List all orders                      |
| `/orders/`             | POST   | `CreateOrderRequest`             | `OrderResponse`        | Create manual order                  |
| `/orders/{id}`         | GET    | -                                | `OrderResponse`        | Get single order                     |
| `/orders/{id}/confirm` | POST   | `{ "message": "string" }`    | `OrderResponse`        | Send confirmation to customer        |
| `/orders/export`       | GET    | -                                | `file`                 | Export orders to CSV                 |

#### Payments (Optional)
| Endpoint               | Method | Request Body                     | Response               | Description                          |
|------------------------|--------|----------------------------------|------------------------|--------------------------------------|
| `/payments/link`       | POST   | `{ "order_id": "string" }`   | `{ "link": "string" }` | Generate Paystack/M-Pesa link   |

#### Dashboard
| Endpoint               | Method | Request Body                     | Response               | Description                          |
|------------------------|--------|----------------------------------|------------------------|--------------------------------------|
| `/dashboard/stats`     | GET    | -                                | `{ "pending": int, "completed": int }` | Order stats |

### Models
```python
class OrderResponse(BaseModel):
    id: str
    customer_name: str
    customer_phone: str
    items: list[dict]  # { "product": str, "quantity": int, "price": float }
    total: float
    status: str  # "pending", "confirmed", "paid", "fulfilled"
    created_at: datetime
    notes: str | None

class CreateOrderRequest(BaseModel):
    message: str  # Raw WhatsApp message text
    customer_phone: str
```

---

## 4. DATABASE SCHEMA (Appwrite Collections)

### Collection: `orders`
```json
{
  "name": "orders",
  "attributes": [
    { "key": "customer_name", "type": "string", "required": true },
    { "key": "customer_phone", "type": "string", "required": true },
    { "key": "items", "type": "json", "required": true },
    { "key": "total", "type": "float", "required": true },
    { "key": "status", "type": "string", "required": true, "default": "pending" },
    { "key": "created_at", "type": "datetime", "required": true },
    { "key": "notes", "type": "string", "required": false },
    { "key": "payment_link", "type": "string", "required": false }
  ],
  "indexes": [
    { "key": "by_customer", "type": "fulltext", "attributes": ["customer_phone"] },
    { "key": "by_status", "type": "key", "attributes": ["status"] },
    { "key": "by_date", "type": "key", "attributes": ["created_at"] }
  ]
}
```

### Collection: `users`
```json
{
  "name": "users",
  "attributes": [
    { "key": "name", "type": "string", "required": true },
    { "key": "phone", "type": "string", "required": true },
    { "key": "whatsapp_connected", "type": "boolean", "required": true, "default": false },
    { "key": "plan", "type": "string", "required": true, "default": "basic" },
    { "key": "paystack_key", "type": "string", "required": false },
    { "key": "mpesa_key", "type": "string", "required": false }
  ],
  "indexes": [
    { "key": "by_phone", "type": "unique", "attributes": ["phone"] }
  ]
}
```

---

## 5. ENVIRONMENT VARIABLES

### Backend
```
# Appwrite
APPWRITE_ENDPOINT="http://100.87.228.1/v1"
APPWRITE_PROJECT_ID="your_project_id"
APPWRITE_API_KEY="your_api_key"
APPWRITE_DATABASE_ID="your_database_id"

# WhatsApp
WHATSAPP_CLOUD_API_KEY="your_meta_api_key"  # Fallback for Cloud API
WHATSAPP_BUSINESS_PHONE_ID="your_phone_id"  # Optional

# Payment Gateways (Optional)
PAYSTACK_SECRET_KEY="your_paystack_key"
MPESA_CONSUMER_KEY="your_mpesa_key"
MPESA_CONSUMER_SECRET="your_mpesa_secret"

# Security
JWT_SECRET="your_jwt_secret"
CORS_ORIGINS="http://localhost:3000,capacitor://localhost"

# FastAPI
APP_HOST="0.0.0.0"
APP_PORT=8000
```

### Frontend
```
VITE_API_URL="http://100.87.228.1:8000/api/v1"
VITE_WHATSAPP_CONNECT_URL="ws://100.87.228.1:8000/whatsapp/ws"
```

---

## 6. MVP FEATURE LIST (STRICT)

### Core
1. **WhatsApp Order Parsing** 
   - Rule-based extraction (e.g., "1× Pizza ₦2000")
   - Handles unstructured messages → flags for manual review
   - Stores in Appwrite `orders` collection

2. **Baileys QR Login** 
   - QR code screen for non-Business WhatsApp users
   - Session persistence
   - Connection status indicator

3. **Auto-Confirmation** 
   - Sends structured reply via WhatsApp
   - Template: "Your order for {items} at ₦{total} is received!"

4. **Merchant Dashboard** 
   - Web view of pending/completed orders
   - CSV export
   - Filter by status

5. **Mobile App** 
   - Scan QR → connect WhatsApp
   - View orders
   - Mark as fulfilled

### Non-MVP (Post-Ship)
- Payment link generation (Paystack/M-Pesa)
- Multi-language support (Swahili)
- Inventory management
- Analytics/reports

---

## 7. AGENT ROSTER

| Agent               | Role                                      | Tools/Access                          |
|---------------------|-------------------------------------------|---------------------------------------|
| **VULCAN**          | Primary backend implementation           | FastAPI, Appwrite, Baileys            |
| **LOOM**            | Frontend (React+Capacitor)                | Stitch, React, Tailwind               |
| **JANUS**           | Deployment + CI/CD                        | Docker, GitHub Actions, EAS           |
| **ALCHEMIST**       | Dependency audit                           | `requirements.txt`, `package.json`    |
| **SENTINEL**        | Security review                            | Static analysis, env validation       |

---

## 8. BUILD TIMELINE

| Phase               | Tasks                                                                 | Time   |
|--------------------|-----------------------------------------------------------------------|--------|
| **Hour 1**         | - Project scaffolding (backend/frontend)
                        - Appwrite collections setup
                        - FastAPI base structure                     | 60m    |
| **Hour 2**         | - Baileys integration (QR code generation)
                        - WhatsApp Cloud API fallback
                        - Order parsing logic                        | 60m    |
| **Hour 3**         | - Appwrite order storage
                        - Order confirmation flow
                        - Merchant dashboard UI                      | 60m    |
| **Hour 4**         | - Capacitor mobile app (QR scanner)
                        - CSV export
                        - Error handling + edge cases                | 60m    |
| **Hour 5**         | - Deployment (Docker + Coolify)
                        - CI/CD setup (GitHub Actions)
                        - Cloud build (EAS)                          | 60m    |
| **Hour 6**         | - Testing (manual + automated)
                        - Documentation (user install guide)
                        - Handoff to SPECTRAL                        | 60m    |

**Total:** 6 hours

---

## 9. KEY DECISIONS

1. **Baileys over WhatsApp Business API**
   - Solves the QR scan requirement for non-Business users
   - Lower cost (no approval needed)
   - Fallback to Cloud API if Baileys fails

2. **Rule-Based Parsing**
   - No ML → faster implementation
   - Handles 80% of African SMB order messages
   - Flags unstructured messages for manual review

3. **Capacitor + React**
   - Single codebase (web + mobile)
   - Android APK generation via EAS
   - Non-technical user distribution

4. **Appwrite Self-Hosted**
   - Aligns with VPS constraint
   - No external database costs
   - Built-in auth and file storage

---

## 10. RISK MITIGATION

| Risk                          | Mitigation Strategy                          |
|-------------------------------|----------------------------------------------|
| WhatsApp bans Baileys        | Fallback to Cloud API + rotate sessions      |
| Parser misses edge cases      | Manual review flag + iterative improvement   |
| Appwrite latency              | Local caching (Redis) + bulk inserts         |
| Non-technical user onboarding | Step-by-step QR guide + video tutorial       |
| Payment gateway failures      | Graceful degradation (order w/o payment)     |