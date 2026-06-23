# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/services/payment_service.py
'''Payment service – generates payment links for confirmed orders.

Supported gateway: Paystack (default). Uses async httpx client.
If settings.PAYSTACK_SECRET_KEY is missing the service raises an error.
'''

from __future__ import annotations

import logging
from typing import Optional

import httpx

from ..config import settings
from .order_service import get_order, attach_payment_link
from ..models.orders import OrderResponse

_logger = logging.getLogger("uvicorn.error")

def _sanitize_email(name: str) -> str:
    """Derive a placeholder email address from a person's name.

    The email is not used for real communication – Paystack requires an email
    field. We generate ``firstname.lastname@example.com`` in lower‑case, dropping
    any non‑alphanumeric characters.

    Unicode names are normalised to ASCII before processing to avoid email
    validity issues (e.g. "Renée" → "Renee").
    """
    import re
    import unicodedata

    try:
        # Normalise Unicode to ASCII (é → e, 中文 → han_ etc.)
        name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    except Exception:
        pass  # Fall back to original name if normalisation fails

    # Normalise whitespace, split into parts, drop empty strings
    parts = [p for p in re.split(r'\s+', name.strip()) if p]
    if not parts:
        return "user@example.com"
    # Take first and last part for email local‑part
    local = f"{parts[0]}.{parts[-1]}".lower()
    # Remove any characters that are not allowed in email local part
    local = re.sub(r'[^a-z0-9._%-]', '', local)
    if not local:
        return "user@example.com"
    return f"{local}@example.com"

async def create_payment_link(order_id: str) -> OrderResponse:
    """Generate a payment link for a confirmed order and store it.

    Steps:
    1. Retrieve the order and verify it is ``confirmed``.
    2. Ensure ``settings.PAYSTACK_SECRET_KEY`` is configured.
    3. Call Paystack ``/transaction/initialize`` to obtain an ``authorization_url``.
    4. Persist the URL to the ``payment_link`` field of the order document.
    5. Return the refreshed ``OrderResponse``.

    Raises:
        FileNotFoundError: If the order does not exist.
        ValueError: If the order is not in ``confirmed`` status.
        RuntimeError: If the Paystack request fails.
    """
    # 1. Load order
    order = await get_order(order_id)
    if order.status != "confirmed":
        raise ValueError("Payment link can only be generated for confirmed orders")

    # 2. Verify Paystack configuration
    secret_key: Optional[str] = settings.PAYSTACK_SECRET_KEY
    if not secret_key:
        raise RuntimeError("Paystack secret key not configured in environment")

    # 3. Prepare request payload – Paystack expects amount in kobo (NGN * 100)
    amount_kobo = int(round(order.total * 100))
    email = _sanitize_email(order.customer_name)
    payload = {
        "email": email,
        "amount": amount_kobo,
        "metadata": {"order_id": order_id},
    }
    headers = {"Authorization": f"Bearer {secret_key}"}
    url = "https://api.paystack.co/transaction/initialize"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
    except Exception as exc:
        _logger.exception("Paystack request failed for order %s", order_id)
        raise RuntimeError(f"Failed to contact payment provider: {exc}")

    if resp.status_code != 200:
        _logger.error(
            "Paystack error %s for order %s: %s",
            resp.status_code,
            order_id,
            resp.text,
        )
        raise RuntimeError(f"Paystack request failed: {resp.status_code} {resp.text}")

    data = resp.json().get("data", {})
    auth_url = data.get("authorization_url")
    if not auth_url:
        raise RuntimeError("Paystack response missing authorization_url")

    # 4. Persist the link in Appwrite
    updated_order = await attach_payment_link(order_id, auth_url)
    return updated_order
