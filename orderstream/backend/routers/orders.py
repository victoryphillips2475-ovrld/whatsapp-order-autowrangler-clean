# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/routers/orders.py
"""Orders router — CRUD for the orders collection.

All routes are protected: a valid JWT must be passed in the
``Authorization: Bearer <token>`` header.
"""

from __future__ import annotations

import csv
import io
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from ..dependencies import get_current_user
from ..models.orders import (
    CreateOrderRequest,
    ConfirmOrderRequest,
    UpdateOrderRequest,
    OrderResponse,
    OrderListResponse,
)
from ..services.order_service import (
    list_orders,
    create_order,
    get_order,
    confirm_order,
    update_order_status,
    update_order,
)
from ..services.whatsapp_service import send_confirmation_message

router = APIRouter(tags=["Orders"])
_logger = logging.getLogger("uvicorn.error")


# ---------------------------------------------------------------------------
# Helper — CSV-safe value (escape commas, newlines, double-quotes)
# ---------------------------------------------------------------------------

def _csv_escape(value: str) -> str:
    """Escape a value for CSV: wrap in quotes if it contains commas, newlines, or quotes."""
    if not value:
        return ""
    if "," in value or "\n" in value or "\r" in value or '"' in value:
        return '"' + value.replace('"', '""') + '"'
    return value


# ---------------------------------------------------------------------------
# Helper — verify order belongs to authenticated user
# ---------------------------------------------------------------------------

async def _verify_order_owner(order_id: str, user: dict) -> OrderResponse:
    """Fetch an order and verify it belongs to the authenticated user.

    Raises HTTPException 404 if the order does not exist, or 403 if it belongs
    to a different user.
    """
    try:
        order = await get_order(order_id)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.user_id and order.user_id != user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this order",
        )
    return order


@router.get("/", response_model=OrderListResponse)
async def list(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    user: dict = Depends(get_current_user),
) -> OrderListResponse:
    """
    List orders for the authenticated merchant.

    Supports filtering by ``status`` (pending | confirmed | fulfilled | cancelled)
    and pagination via ``page`` / ``page_size``.
    Only returns orders belonging to the authenticated user.
    """
    offset = (page - 1) * page_size
    orders = await list_orders(
        status=status_filter, limit=page_size, offset=offset, user_id=user["user_id"]
    )
    return OrderListResponse(orders=orders, total=len(orders), page=page, page_size=page_size)


@router.get("/export")
async def export(
    status_filter: Optional[str] = Query(None, alias="status"),
    user: dict = Depends(get_current_user),
) -> StreamingResponse:
    """
    Export orders as a CSV file.

    Supports the same ``status`` filter as the list endpoint.
    Only exports orders belonging to the authenticated user.
    """
    orders = await list_orders(
        status=status_filter, limit=10000, user_id=user["user_id"]
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Customer", "Phone", "Items", "Total (₦)", "Status", "Created At", "Notes"])
    for order in orders:
        items_str = "; ".join(f"{it.quantity}x {it.product} @ ₦{it.price}" for it in order.items)
        writer.writerow([
            order.id,
            _csv_escape(order.customer_name),
            _csv_escape(order.customer_phone),
            items_str,
            order.total,
            order.status,
            order.created_at.isoformat(),
            _csv_escape(order.notes or ""),
        ])
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders_export.csv"},
    )


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create(
    payload: CreateOrderRequest,
    user: dict = Depends(get_current_user),
) -> OrderResponse:
    """Create a new order manually (without going through WhatsApp).

    The order is always attributed to the authenticated merchant — the
    ``user_id`` field in the request body is ignored to prevent impersonation.
    """
    payload.user_id = user["user_id"]
    try:
        return await create_order(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        _logger.exception("Order creation failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create order")


@router.put("/{order_id}", response_model=OrderResponse)
async def update(
    order_id: str,
    payload: UpdateOrderRequest,
    user: dict = Depends(get_current_user),
) -> OrderResponse:
    """Update an existing order (partial update — only provided fields are changed).

    The authenticated user must own the order.
    """
    # Verify ownership first
    await _verify_order_owner(order_id, user)

    try:
        return await update_order(
            order_id=order_id,
            customer_name=payload.customer_name,
            customer_phone=payload.customer_phone,
            items=[item.dict() for item in payload.items] if payload.items else None,
            notes=payload.notes,
            status=payload.status,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        _logger.exception("Order update failed for %s", order_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update order")


@router.get("/{order_id}", response_model=OrderResponse)
async def get(
    order_id: str,
    user: dict = Depends(get_current_user),
) -> OrderResponse:
    """Fetch a single order by its ID. User must own the order."""
    return await _verify_order_owner(order_id, user)


@router.post("/{order_id}/confirm", response_model=OrderResponse)
async def confirm(
    order_id: str,
    payload: ConfirmOrderRequest,
    user: dict = Depends(get_current_user),
) -> OrderResponse:
    """
    Mark an order as confirmed and (optionally) send a WhatsApp message
    to the customer with a custom confirmation text.
    """
    order = await _verify_order_owner(order_id, user)

    try:
        await confirm_order(order_id, payload.message)
    except Exception as exc:
        _logger.exception("Order confirmation failed for %s", order_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to confirm order")

    # Send optional WhatsApp message
    if payload.message:
        try:
            await send_confirmation_message(order.customer_phone, payload.message)
        except Exception:
            pass  # Non‑fatal: order is confirmed regardless

    return await get_order(order_id)


@router.post("/{order_id}/fulfill", response_model=OrderResponse)
async def fulfill(
    order_id: str,
    user: dict = Depends(get_current_user),
) -> OrderResponse:
    """Mark an order as fulfilled/delivered."""
    await _verify_order_owner(order_id, user)
    try:
        await update_order_status(order_id, "fulfilled")
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    except Exception as exc:
        _logger.exception("Order fulfillment failed for %s", order_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fulfill order")

    return await get_order(order_id)