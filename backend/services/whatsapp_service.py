"""Service layer for WhatsApp Baileys integration.

The current implementation is a **placeholder** that stores QR codes in memory
and provides a stub for sending confirmation messages.
Replace with real Baileys session handling and WhatsApp Cloud API calls for production.
"""

import base64
import io
import logging
import time
from typing import Dict, Optional

import qrcode

from ..config import settings

_logger = logging.getLogger("uvicorn.error")

# In‑memory store (user_id -> {status, qr, updated_at})
_STORE: Dict[str, Dict[str, str | float]] = {}
_SESSION_TTL_SECONDS = 300  # 5 minutes — stale entries pruned on access
_LAST_PRUNE_TIME: float = 0.0
_PRUNE_INTERVAL_SECONDS = 30.0  # Only prune every 30 seconds


def _prune_expired():
    """Remove entries older than _SESSION_TTL_SECONDS. Runs at most once per _PRUNE_INTERVAL_SECONDS."""
    global _LAST_PRUNE_TIME
    now = time.monotonic()
    if now - _LAST_PRUNE_TIME < _PRUNE_INTERVAL_SECONDS:
        return  # Skip pruning — too soon
    _LAST_PRUNE_TIME = now
    expired = [k for k, v in _STORE.items() if now - v.get("updated_at", 0) > _SESSION_TTL_SECONDS]
    for k in expired:
        del _STORE[k]


def generate_qr(session_id: str) -> str:
    """Generate a QR code image for the given session and return a base64 string.

    The QR payload is a simple placeholder URL containing the session_id.
    In production, replace this with a real Baileys QR code generation.
    """
    _prune_expired()
    data = f"whatsapp://connect?session={session_id}"
    img = qrcode.make(data)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_b64 = base64.b64encode(buffered.getvalue()).decode()
    _STORE[session_id] = {"status": "pending", "qr": qr_b64, "updated_at": time.monotonic()}
    return qr_b64


def get_status(session_id: str) -> str:
    """Return the connection status for the session (pending/connected/unknown)."""
    _prune_expired()
    return _STORE.get(session_id, {}).get("status", "unknown")


def set_connected(session_id: str) -> None:
    """Mark the session as connected. In a real implementation this would be
    called by Baileys connection events.
    """
    _prune_expired()
    if session_id in _STORE:
        _STORE[session_id]["status"] = "connected"
        _STORE[session_id]["updated_at"] = time.monotonic()


def set_disconnected(session_id: str) -> None:
    """Mark the session as disconnected."""
    _prune_expired()
    if session_id in _STORE:
        _STORE[session_id]["status"] = "disconnected"
        _STORE[session_id]["updated_at"] = time.monotonic()


async def send_confirmation_message(to_phone: str, message: str) -> None:
    """
    Send a plain‑text WhatsApp confirmation message to a customer.

    **Current implementation is a placeholder** — logs the message but does not
    deliver it. In production, integrate with the WhatsApp Cloud API (POST /messages)
    or Baileys ``sendMessage``.
    """
    _logger.info("[WhatsApp] Confirmation to %s: %s", to_phone, message)
    # No‑op for now; replace with real provider when credentials are configured.
    return None
