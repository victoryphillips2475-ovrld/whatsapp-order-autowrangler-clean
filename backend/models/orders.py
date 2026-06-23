# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/models/orders.py
"""Order Pydantic models — request/response schemas for the orders API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    """Single line item within an order."""

    product: str = Field(..., min_length=1, max_length=200)
    quantity: int = Field(..., ge=1, description="Number of units ordered")
    price: float = Field(..., ge=0, description="Unit price in Naira")


class CreateOrderRequest(BaseModel):
    """Request to create an order manually (bypassing WhatsApp) or via webhook."""

    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_phone: str = Field(..., min_length=1, max_length=20)
    items: list[OrderItem] = Field(..., min_length=1)
    notes: Optional[str] = Field(None, max_length=500)
    user_id: Optional[str] = Field(
        None,
        description="Owner merchant ID. Required for orders to be retrievable via the API.",
    )


class ConfirmOrderRequest(BaseModel):
    """Optional message to send to customer when confirming an order."""

    message: Optional[str] = Field(None, max_length=500)


class UpdateOrderRequest(BaseModel):
    """Request to update an existing order. All fields are optional — only
    provided fields are updated (partial update semantics)."""

    customer_name: Optional[str] = Field(None, min_length=1, max_length=100)
    customer_phone: Optional[str] = Field(None, min_length=1, max_length=20)
    items: Optional[list[OrderItem]] = Field(None, min_length=1)
    notes: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(
        None,
        description="One of: pending | confirmed | paid | fulfilled | cancelled",
    )


class OrderResponse(BaseModel):
    """Single order as returned by the API."""

    id: str
    customer_name: str
    customer_phone: str
    items: list[OrderItem]
    total: float = Field(..., description="Total order value in Naira")
    status: str = Field(
        ...,
        description="One of: pending | confirmed | paid | fulfilled | cancelled",
    )
    created_at: datetime
    notes: Optional[str] = None
    payment_link: Optional[str] = None


class OrderListResponse(BaseModel):
    """Paginated list of orders."""

    orders: list[OrderResponse]
    total: int
    page: int = 1
    page_size: int = 100