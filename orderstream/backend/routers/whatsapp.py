# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/routers/whatsapp.py
"""WhatsApp router — Baileys QR code, session management, and incoming webhook.

These endpoints are used by the mobile app to:
  1. Obtain a QR code for the authenticated merchant to scan with WhatsApp.
  2. Check connection status.
  3. Disconnect the session.
  4. Receive inbound messages from Baileys (webhook).

Rate limiting on QR generation is enforced at nginx level.
The WhatsApp Cloud API (send message) is handled separately in
``services/whatsapp_service.py`` which is called by the orders router.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..dependencies import get_current_user
from ..services.whatsapp_service import generate_qr, get_status, set_connected, set_disconnected

router = APIRouter(tags=["WhatsApp"])
_logger = logging.getLogger("uvicorn.error")


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class QRResponse(BaseModel):
    """Response containing a base64‑encoded QR code PNG."""

    qr_code_base64: str
    session_id: str
    expires_in: int = 90  # seconds until the QR expires


class StatusResponse(BaseModel):
    """Current WhatsApp connection status for the authenticated merchant."""

    connected: bool
    phone: str | None = None


# ---------------------------------------------------------------------------
# QR & session endpoints
# ---------------------------------------------------------------------------


def _session_id_for_user(user: dict) -> str:
    """Derive a per-user WhatsApp session key from the authenticated user."""
    # Use user ID to isolate each merchant's WhatsApp session
    return f"wa_{user['user_id']}"


@router.get("/qr", response_model=QRResponse)
async def get_qr_code(
    user: dict = Depends(get_current_user),
) -> QRResponse:
    """
    Generate a fresh QR code for the merchant to scan with WhatsApp.

    The QR code is generated using the Baileys library in
    ``services/whatsapp_service.py``. The current implementation is a **stub**
    that returns a placeholder QR — replace with real Baileys session start.

    The QR code expires after 90 seconds. The mobile app should poll this
    endpoint until ``GET /whatsapp/status`` returns ``connected: true``.
    """
    session_id = _session_id_for_user(user)
    try:
        qr_b64 = generate_qr(session_id)
        return QRResponse(qr_code_base64=qr_b64, session_id=session_id, expires_in=90)
    except Exception as exc:
        _logger.exception("QR generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate QR code",
        ) from exc


@router.get("/status", response_model=StatusResponse)
async def get_connection_status(
    user: dict = Depends(get_current_user),
) -> StatusResponse:
    """
    Return the current WhatsApp connection status for the authenticated merchant.

    Poll this endpoint after scanning the QR code to know when the
    session is active (``connected: true``).
    """
    session_id = _session_id_for_user(user)
    raw_status = get_status(session_id)
    return StatusResponse(connected=(raw_status == "connected"), phone=None)


@router.post("/disconnect")
async def disconnect(
    user: dict = Depends(get_current_user),
) -> dict:
    """
    Disconnect the active WhatsApp Baileys session.

    This clears the in‑memory session store. In production, also call
    ``baileys sock.logout()`` to invalidate the WA Web session properly.
    """
    session_id = _session_id_for_user(user)
    set_disconnected(session_id)
    _logger.info("WhatsApp session %s disconnected", session_id)
    return {"message": "WhatsApp disconnected"}