# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/services/order_service.py
"""Order service – interacts with Appwrite using a thread‑pool wrapper.

The Appwrite Python SDK is synchronous. To keep the FastAPI endpoints fully
async we execute the SDK calls inside ``run_in_threadpool`` which off‑loads the
blocking I/O to a worker thread while preserving FastAPI's concurrency model.

The service also provides a lightweight health‑check function used by the
readiness probe.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import List, Optional

from fastapi.concurrency import run_in_threadpool

from appwrite.client import Client
from appwrite.query import Query
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException
from uuid import uuid4

from ..config import settings
from ..models.orders import OrderResponse, OrderItem, CreateOrderRequest

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------
_NAIRA_SYMBOL = "\u20a6"  # ₦ — Nigerian Naira currency symbol
_ORDER_PATTERN = re.compile(r"(\d+)x\s+([^\s]+)\s+" + _NAIRA_SYMBOL + r"([\d.]+)")

# Valid status values for the Appwrite `equal()` query filter.
_VALID_STATUSES = frozenset({"pending", "confirmed", "paid", "fulfilled", "cancelled"})
# A status must be alphanumeric + hyphen/underscore only, max 32 chars.
_STATUS_RE = re.compile(r"^[a-zA-Z0-9_-]{1,32}$")

# ---------------------------------------------------------------------------
# Initialise a single shared Appwrite client – configuration is validated by
# ``settings`` at import time.
# ---------------------------------------------------------------------------
_client = Client()
_client.set_endpoint(settings.APPWRITE_ENDPOINT)
_client.set_project(settings.APPWRITE_PROJECT_ID)
_client.set_key(settings.APPWRITE_API_KEY)

_db = Databases(_client)
__COLLECTION_ID = "orders"

# A small thread‑pool for blocking SDK calls. The pool size mirrors the
# number of workers that the UVicorn server is configured with (default 4).
# Note: We use FastAPI's run_in_threadpool instead of this executor directly.


# ---------------------------------------------------------------------------
# Helper – synchronous wrapper used by ``run_in_threadpool``.
# ---------------------------------------------------------------------------
def _list_documents_sync(
    limit: int = 100, offset: int = 0, status: Optional[str] = None,
    user_id: Optional[str] = None,
) -> dict:
    """Synchronously call ``list_documents`` with optional pagination,
    status filtering, and user scoping.
    """
    queries = [Query.limit(limit), Query.offset(offset)]
    if status:
        # Reject values that would break the Appwrite query language or inject.
        if not _STATUS_RE.fullmatch(status) or status not in _VALID_STATUSES:
            status = None
        else:
            queries.append(Query.equal("status", status))
    if user_id:
        queries.append(Query.equal("user_id", user_id))
    return _db.list_documents(settings.APPWRITE_DATABASE_ID, _COLLECTION_ID, queries=queries)


def _create_document_sync(doc: dict) -> dict:
    return _db.create_document(settings.APPWRITE_DATABASE_ID, _COLLECTION_ID, uuid4().hex, doc)


def _get_document_sync(order_id: str) -> dict:
    return _db.get_document(settings.APPWRITE_DATABASE_ID, _COLLECTION_ID, order_id)


def _update_document_sync(order_id: str, updates: dict) -> dict:
    return _db.update_document(settings.APPWRITE_DATABASE_ID, _COLLECTION_ID, order_id, updates)


# ---------------------------------------------------------------------------
# Public async API
# ---------------------------------------------------------------------------
async def list_orders(
    status: Optional[str] = None, limit: int = 100, offset: int = 0,
    user_id: Optional[str] = None,
) -> List[OrderResponse]:
    """Return a list of ``OrderResponse`` objects.

    Args:
        status: Optional status filter (e.g. ``"pending"``).
        limit: Max number of rows – capped to 1000 for safety.
        offset: Number of rows to skip.
        user_id: When provided, only return orders belonging to this merchant.
    """
    # Clamp limits to a sane range.
    limit = max(1, min(limit, 1000))
    offset = max(0, offset)
    try:
        raw = await run_in_threadpool(
            _list_documents_sync, limit=limit, offset=offset, status=status,
            user_id=user_id,
        )
    except AppwriteException as exc:
        logging.getLogger("uvicorn.error").error(f"Appwrite list_documents failed: {exc}")
        raise

    results: List[OrderResponse] = []
    for doc in raw.get("documents", []):
        # The SDK returns timestamps in ISO‑8601 format.
        created_at = datetime.fromisoformat(doc["created_at"]).replace(tzinfo=timezone.utc)
        items = [OrderItem(**it) for it in doc.get("items", [])]
        order = OrderResponse(
            id=doc["$id"],
            customer_name=doc.get("customer_name", ""),
            customer_phone=doc.get("customer_phone", ""),
            items=items,
            total=doc.get("total", 0.0),
            status=doc.get("status", "pending"),
            created_at=created_at,
            notes=doc.get("notes"),
        )
        results.append(order)
    return results


async def create_order(request: CreateOrderRequest) -> OrderResponse:
    """
    Create and persist a new order.

    For WhatsApp‑origin orders the ``message`` field carries the raw text which
    is parsed with the regex pattern. For manually‑created orders ``items`` is
    already a structured list.
    """
    items: list[dict] = []
    total = 0.0

    if request.items:
        # Structured order (from manual create or parsed WhatsApp)
        for it in request.items:
            items.append({"product": it.product, "quantity": it.quantity, "price": it.price})
            total += it.quantity * it.price
    elif request.message:
        # Raw‑text WhatsApp message — use the regex parser
        for line in request.message.splitlines():
            match = _ORDER_PATTERN.search(line)
            if match:
                qty = int(match.group(1))
                product = match.group(2)
                price = float(match.group(3))
                items.append({"product": product, "quantity": qty, "price": price})
                total += qty * price

    if not items:
        raise ValueError("No items could be extracted from the order request")

    doc = {
        "customer_name": request.customer_name,
        "customer_phone": request.customer_phone,
        "items": items,
        "total": total,
        "status": "pending",
        "created_at": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        "notes": request.notes or "",
    }
    if request.user_id:
        doc["user_id"] = request.user_id
    try:
        result = await run_in_threadpool(_create_document_sync, doc)
    except AppwriteException as exc:
        logging.getLogger("uvicorn.error").error(f"Appwrite create_document failed: {exc}")
        raise
    return await get_order(result["$id"])


async def confirm_order(order_id: str, message: str) -> bool:
    """Mark an order as ``confirmed`` and store an optional note.

    Returns ``True`` on success.
    """
    try:
        _ = await run_in_threadpool(_get_document_sync, order_id)
        updates = {"status": "confirmed"}
        if message:
            updates["notes"] = message
        await run_in_threadpool(_update_document_sync, order_id, updates)
        return True
    except AppwriteException as exc:
        logging.getLogger("uvicorn.error").error(f"Appwrite update failed for {order_id}: {exc}")
        raise


async def update_order(order_id: str, customer_name: Optional[str] = None,
                       customer_phone: Optional[str] = None, items: Optional[List[dict]] = None,
                       notes: Optional[str] = None, status: Optional[str] = None) -> OrderResponse:
    """Partially update an order.

    Args:
        order_id: ID of the order to update.
        customer_name: New customer name (optional).
        customer_phone: New customer phone (optional).
        items: New items list (optional).
        notes: New notes (optional).
        status: New status (optional).

    Returns:
        Updated OrderResponse.

    Raises:
        FileNotFoundError: If the order does not exist.
        ValueError: If the status value is not recognised.
    """
    if status is not None and status not in _VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {_VALID_STATUSES}")

    try:
        # Verify order exists
        await run_in_threadpool(_get_document_sync, order_id)

        updates: dict[str, object] = {}
        if customer_name is not None:
            updates["customer_name"] = customer_name
        if customer_phone is not None:
            updates["customer_phone"] = customer_phone
        if items is not None:
            total = sum(item["quantity"] * item["price"] for item in items)
            updates["items"] = items
            updates["total"] = total
        if notes is not None:
            updates["notes"] = notes
        if status is not None:
            updates["status"] = status

        if updates:
            await run_in_threadpool(_update_document_sync, order_id, updates)
    except AppwriteException as exc:
        if exc.code == 404:
            raise FileNotFoundError(f"Order {order_id} not found")
        logging.getLogger("uvicorn.error").error(f"Appwrite update failed for {order_id}: {exc}")
        raise

    return await get_order(order_id)


async def get_order(order_id: str) -> OrderResponse:
    """Fetch a single order by its Appwrite document ID.

    Raises:
        FileNotFoundError: If the document does not exist.
    """
    try:
        doc = await run_in_threadpool(_get_document_sync, order_id)
    except AppwriteException as exc:
        if exc.code == 404:
            raise FileNotFoundError(f"Order {order_id} not found")
        raise

    created_at = datetime.fromisoformat(doc["created_at"]).replace(tzinfo=timezone.utc)
    items = [OrderItem(**it) for it in doc.get("items", [])]
    return OrderResponse(
        id=doc["$id"],
        customer_name=doc.get("customer_name", ""),
        customer_phone=doc.get("customer_phone", ""),
        items=items,
        total=doc.get("total", 0.0),
        status=doc.get("status", "pending"),
        created_at=created_at,
        notes=doc.get("notes"),
        payment_link=doc.get("payment_link"),
    )



async def update_order_status(order_id: str, new_status: str) -> None:
    """
    Update the status field of an order.

    Raises:
        FileNotFoundError: If the order does not exist.
        ValueError: If the status value is not recognised.
    """
    if new_status not in _VALID_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'. Must be one of: {_VALID_STATUSES}")

    try:
        await run_in_threadpool(_get_document_sync, order_id)
        await run_in_threadpool(_update_document_sync, order_id, {"status": new_status})
    except AppwriteException as exc:
        if exc.code == 404:
            raise FileNotFoundError(f"Order {order_id} not found")
        logging.getLogger("uvicorn.error").error(f"Appwrite status update failed for {order_id}: {exc}")
        raise


# ---------------------------------------------------------------------------
# Payment link attachment helper – updates Appwrite order with payment URL.
# ---------------------------------------------------------------------------

async def attach_payment_link(order_id: str, payment_link: str) -> OrderResponse:
    """Attach a payment link URL to an order record.

    Raises:
        FileNotFoundError: If the order does not exist.
    Returns the updated OrderResponse.
    """
    try:
        # Ensure order exists before updating
        await run_in_threadpool(_get_document_sync, order_id)
    except AppwriteException as exc:
        if exc.code == 404:
            raise FileNotFoundError(f"Order {order_id} not found")
        raise

    await run_in_threadpool(_update_document_sync, order_id, {"payment_link": payment_link})
    return await get_order(order_id)

# ---------------------------------------------------------------------------
# Readiness helper – used by the ``/ready`` endpoint.
# ---------------------------------------------------------------------------
async def _verify_appwrite_connection() -> bool:
    """Perform a cheap Appwrite call to confirm connectivity.
    Returns ``True`` if the call succeeds, ``False`` otherwise.
    """
    try:
        await run_in_threadpool(_list_documents_sync, limit=1, offset=0)
        return True
    except Exception:
        return False
