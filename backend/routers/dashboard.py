# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/routers/dashboard.py
"""Dashboard router – provides summary statistics for the merchant view.

All routes are protected with JWT authentication.
Rate limiting is handled at nginx level (limit_req_zone=api in nginx.conf).
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ..services.dashboard_service import get_stats
from ..dependencies import get_current_user

router = APIRouter()
_logger = logging.getLogger("uvicorn.error")


@router.get("/stats", response_model=dict)
async def stats(user: dict = Depends(get_current_user)):
    try:
        return await get_stats(user_id=user.get("user_id"))
    except Exception as exc:
        _logger.exception("Dashboard stats failed for user %s", user.get("user_id"))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
