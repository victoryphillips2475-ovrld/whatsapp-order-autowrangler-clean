"""Order parser service – extracts structured data from raw WhatsApp order messages.

The parser is rule‑based with regular‑expression helpers. It extracts:
- ``customer_name`` – name line (e.g. ``Name: John Doe``)
- ``customer_phone`` – phone line (e.g. ``Phone: +2348012345678``)
- ``items`` – a list of dicts ``{"product": str, "quantity": int, "price": float}``
- ``total`` – explicit total line or calculated from items
- ``notes`` – optional free‑form notes after a ``Notes:`` marker

If required fields are missing a ``ValueError`` is raised.
"""

from __future__ import annotations

import logging
import re
from typing import List, Mapping, Optional

_logger = logging.getLogger("uvicorn.error")

# ---------------------------------------------------------------------------
# Regular expression patterns (case‑insensitive)
# ---------------------------------------------------------------------------
_NAME_RE = re.compile(r"^\s*(?:name|customer)\s*[:\-]\s*(?P<value>.+?)\s*$", re.I)
_PHONE_RE = re.compile(r"^\s*(?:phone|contact|mobile)\s*[:\-]\s*(?P<value>\+?[\d\s\-().]+)\s*$", re.I)
_TOTAL_RE = re.compile(r"^\s*total\s*[:\-]?\s*₦?\s*(?P<value>[\d,.]+)\s*$", re.I)
_NOTES_RE = re.compile(r"^\s*notes?\s*[:\-]\s*(?P<value>.+?)\s*$", re.I)
# Item line – e.g. "2x Coke ₦150" or "1 x Bread 200"
_ITEM_RE = re.compile(
    r"^\s*(?P<qty>\d+)\s*x\s+(?P<product>.+?)\s+(?:₦|NGN)?\s*(?P<price>[\d,.]+)\s*$",
    re.I,
)

# ---------------------------------------------------------------------------
# Helper functions – each returns ``None`` if not found.
# ---------------------------------------------------------------------------

def _extract_first_match(pattern: re.Pattern[str], lines: List[str]) -> Optional[str]:
    for line in lines:
        m = pattern.match(line)
        if m:
            return m.group("value").strip()
    return None


def _extract_items(lines: List[str]) -> List[Mapping[str, object]]:
    items: List[Mapping[str, object]] = []
    for line in lines:
        m = _ITEM_RE.match(line)
        if m:
            qty = int(m.group("qty"))
            product = m.group("product").strip()
            # Normalise price – remove commas and convert to float
            price_raw = m.group("price").replace(",", "")
            price = float(price_raw)
            items.append({"product": product, "quantity": qty, "price": price})
    return items


def _normalise_phone(raw: str) -> str:
    # Strip everything except digits and leading plus
    cleaned = re.sub(r"[^\d+]", "", raw)
    # Ensure it starts with '+' – if not, assume local number and prepend '+'
    if not cleaned.startswith("+"):
        cleaned = f"+{cleaned}"
    return cleaned

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_MAX_MESSAGE_LENGTH = 10 * 1024  # 10 KB – max inbound WhatsApp message size


def parse_whatsapp_order(message: str) -> Mapping[str, object]:
    """Parse a raw WhatsApp order message.

    The function returns a mapping with the following keys:
    ``customer_name`` (str), ``customer_phone`` (str), ``items`` (list of dicts),
    ``total`` (float), and ``notes`` (str | None).

    ``ValueError`` is raised when mandatory fields (name, phone, items) cannot be
    extracted, or when the message exceeds 10 KB.
    """
    if not isinstance(message, str):
        raise TypeError("message must be a string")

    if len(message) > _MAX_MESSAGE_LENGTH:
        raise ValueError(f"message exceeds maximum length of {_MAX_MESSAGE_LENGTH} characters")

    lines = [ln.strip() for ln in message.splitlines() if ln.strip()]
    if not lines:
        raise ValueError("empty message supplied")

    customer_name = _extract_first_match(_NAME_RE, lines)
    customer_phone_raw = _extract_first_match(_PHONE_RE, lines)
    total_raw = _extract_first_match(_TOTAL_RE, lines)
    notes_raw = _extract_first_match(_NOTES_RE, lines)
    items = _extract_items(lines)

    if not customer_name:
        raise ValueError("customer name not found in message")
    if not customer_phone_raw:
        raise ValueError("customer phone not found in message")
    if not items:
        raise ValueError("no order items could be parsed from message")

    customer_phone = _normalise_phone(customer_phone_raw)
    total = float(total_raw.replace(",", "")) if total_raw else sum(i["quantity"] * i["price"] for i in items)
    notes = notes_raw if notes_raw else None

    _logger.debug(
        "Parsed WhatsApp order – name=%s phone=%s items=%d total=%s notes=%s",
        customer_name,
        customer_phone,
        len(items),
        total,
        "present" if notes else "absent",
    )

    return {
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "items": items,
        "total": total,
        "notes": notes,
    }

__all__ = ["parse_whatsapp_order"]
