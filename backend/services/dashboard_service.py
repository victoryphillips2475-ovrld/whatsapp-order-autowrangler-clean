"""Dashboard service – simple aggregation over orders."""

from collections import Counter
from typing import Optional
from .order_service import list_orders

async def get_stats(user_id: Optional[str] = None) -> dict:
    """Return per-status order counts for a given merchant.

    Args:
        user_id: When provided, only aggregate orders belonging to this merchant.
    """
    all_orders = await list_orders(limit=1000, user_id=user_id)
    counts = Counter(o.status for o in all_orders)
    return {
        "pending": counts.get("pending", 0),
        "confirmed": counts.get("confirmed", 0),
        "completed": counts.get("fulfilled", 0),
        "cancelled": counts.get("cancelled", 0),
    }
