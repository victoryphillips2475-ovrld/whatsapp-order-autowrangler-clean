# WhatsApp Order Auto‑Wrangler – Privacy Policy

**Last Updated:** 2026-06-18

---

## 1. What Data We Collect
- **WhatsApp data:** phone number, name (if provided), full message content used for order parsing.
- **Account data:** email (if you sign up for the dashboard), JWT token, profile information.
- **Order data:** items, quantities, prices, order status, timestamps, and any notes you add.
- **Device & usage data:** IP address, browser User‑Agent, cookies, and analytics logs.
- **Payment data:** transaction identifiers and status from Paystack or M‑Pesa (we never store raw card details; the gateways handle sensitive payment information).

## 2. How We Use Your Data
- **Order fulfillment:** parsing messages, storing orders, sending confirmation replies via WhatsApp.
- **Service operation:** authentication, authorization, and session management.
- **Communications:** email or in‑app notifications about order status, system updates, or support.
- **Analytics & improvements:** aggregated, anonymised usage statistics to improve the service.
- **Payment processing:** pass necessary identifiers to Paystack/M‑Pesa to generate payment links and confirm payments.

## 3. Lawful Basis for Processing

We process personal data based on the following legal bases:

- **WhatsApp data:** Necessary for contract performance (order parsing service) and legitimate interest in providing the service.
- **Account data:** Necessary for contract performance (authentication) and, where applicable, consent (e.g., newsletter sign‑up).
- **Order data:** Necessary for contract performance (order fulfillment) and compliance with legal obligations.
- **Device & usage data:** Legitimate interests (service improvement, security, analytics) and, for analytics, your consent.
- **Payment data:** Necessary for contract performance and compliance with financial regulations.

We host data on servers located in Nigeria. International transfers are protected by Standard Contractual Clauses.

## 4. Who We Share Your Data With
- **Appwrite (self‑hosted):** stores order and user records.
- **Payment gateways (Paystack, M‑Pesa):** only the minimal identifiers required to create and verify payment links.
- **WhatsApp Cloud API / Baileys library:** messages are forwarded to WhatsApp for delivery; we do not store the raw WhatsApp payload beyond the order parsing step.
- **Hosting provider (Coolify VPS):** for server monitoring and logs.
- **Legal authorities:** if required by law or to protect our rights.

## 5. Data Retention
- **Orders & user profiles:** retained for **5 years** or until you request deletion, whichever is earlier.
- **Analytics logs:** retained for **90 days**.
- **Payment transaction records:** retained for **2 years** to comply with financial regulations.

## 6. Your Rights
- **Access:** request a copy of your data by contacting support.
- **Correction:** ask to amend inaccurate information.
- **Deletion:** you may request removal of your personal data; we will delete your account and associated orders, except where retention is required by law.
- **Portability:** we can provide a CSV export of your orders on request.

## 7. Cookies
We use essential session cookies to maintain your login state. No advertising or third‑party tracking cookies are set. If analytics are enabled, an optional analytics cookie may be used; you can disable it in your browser settings.

## 8. Security Measures
- All traffic is encrypted with TLS 1.2+.
- Passwords and JWT secrets are stored using industry‑standard hashing.
- Access to the Appwrite database is restricted by IP whitelisting.
- Regular security audits are performed by the SENTINEL agent.

## 9. Children’s Privacy
WOAW is not intended for users under **13 years of age** (or under **16** in the EU/UK). We do not knowingly collect personal data from children.

## 10. Contact for Privacy Requests
Please direct all privacy‑related inquiries to **support@woaw.com**. For data protection matters, you may contact our Data Protection Officer at **dpo@woaw.com**.
