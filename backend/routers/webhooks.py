# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/routers/webhooks.py
"""Webhook router — public endpoints called by external services.

Webhooks are authenticated via ``X-Webhook-Secret`` header (shared secret
from ``settings.WEBHOOK_SECRET``) rather than merchant JWT.

Routes herein:
  - ``POST /incoming`` – WhatsApp incoming message webhook from Baileys Node.
"""

from __future__ import annotations

import logging
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from ..config import settings
from ..models.orders import CreateOrderRequest, OrderResponse
from ..services.order_parser_service import parse_whatsapp_order
from ..services.order_service import create_order

router = APIRouter(tags=["Webhooks"])
_logger = logging.getLogger("uvicorn.error")


# ---------------------------------------------------------------------------
# Auth dependency – shared secret
# ---------------------------------------------------------------------------

async def verify_webhook_secret(
    x_webhook_secret: str = Header(..., alias="X-Webhook-Secret"),
) -> None:
    """Reject requests that don't carry the configured webhook secret."""
    expected = settings.WEBHOOK_SECRET
    if not expected:
        _logger.warning("WEBHOOK_SECRET is not configured — webhook disabled")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    if not secrets.compare_digest(x_webhook_secret, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class IncomingMessage(BaseModel):
    """Payload forwarded by the Baileys Node service.

    ``from`` is the remote JID (e.g. ``1234567890@s.whatsapp.net``). ``body`` is
    the raw text message. ``timestamp`` is a Unix epoch integer – optional for
    order creation but retained for logging.
    """

    from_: str = Field(..., alias="from")
    body: str
    timestamp: int | None = None

    class Config:
        allow_population_by_field_name = True


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post(
    "/incoming",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_webhook_secret)],
)
async def incoming_whatsapp_message(message: IncomingMessage) -> OrderResponse:
    """Receive a webhook from the Baileys service, parse the order, and store it.

    Steps:
    1. Parse the raw ``body`` using :func:`parse_whatsapp_order`.
    2. Build a :class:`CreateOrderRequest` from the parsed data.
    3. Persist the order via :func:`create_order`.
    4. Return the created :class:`OrderResponse`.

    Note: Orders created via webhook require ``settings.WEBHOOK_DEFAULT_USER_ID`` to be set.
    If not configured, the endpoint returns 503 to prevent orders from being created without an owner.
    """
    if not settings.WEBHOOK_DEFAULT_USER_ID:
        _logger.error("Webhook attempted without WEBHOOK_DEFAULT_USER_ID configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook processing unavailable: WEBHOOK_DEFAULT_USER_ID not configured"
        )
    try:
        parsed = parse_whatsapp_order(message.body)
    except (ValueError, TypeError) as exc:
        _logger.error("Failed to parse incoming WhatsApp order: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    order_req = CreateOrderRequest(
        customer_name=parsed["customer_name"],
        customer_phone=parsed["customer_phone"],
        items=parsed["items"],
        notes=parsed.get("notes"),
        user_id=settings.WEBHOOK_DEFAULT_USER_ID,  # May be None; document this gap
    )

    order = await create_order(order_req)
    return order