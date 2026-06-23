# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/routers/payments.py
"""Payments router – generates payment links for confirmed orders.

Integrates with Paystack via :func:`payment_service.create_payment_link`.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from ..dependencies import get_current_user
from ..services.payment_service import create_payment_link
from ..models.orders import OrderResponse

router = APIRouter(tags=["Payments"])

class PaymentLinkRequest(BaseModel):
    order_id: str

@router.post("/link", response_model=OrderResponse)
async def create_link(
    req: PaymentLinkRequest,
    _: dict = Depends(get_current_user),
) -> OrderResponse:
    """Generate a payment link for a confirmed order.

    Returns the updated :class:`OrderResponse` containing the ``payment_link`` field.
    """
    try:
        return await create_payment_link(req.order_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    except ValueError as exc:
        # Order not confirmed or other validation error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except RuntimeError as exc:
        # Underlying payment‑provider failure
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )
