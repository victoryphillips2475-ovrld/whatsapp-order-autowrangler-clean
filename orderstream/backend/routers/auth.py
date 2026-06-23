# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/routers/auth.py
"""Auth router — registration, login, logout.

All routes here are PUBLIC (no JWT required) so new merchants can sign up
and existing ones can obtain a token before hitting protected routes.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request

from ..config import settings
from ..dependencies import get_current_user
from ..limiter import limiter
from ..models.users import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)
from ..services.auth_service import authenticate_user, register_user, get_user_by_id

router = APIRouter(prefix="", tags=["auth"])
_logger = logging.getLogger("uvicorn.error")


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(limiter.limit("10/minute"))])
async def register(payload: UserRegisterRequest) -> UserResponse:
    """
    Register a new merchant account.

    Returns the created user profile. Use ``POST /auth/login`` afterwards to obtain a JWT.
    """
    try:
        user = await register_user(payload)
        return user
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except Exception as exc:
        _logger.exception("Registration failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")


@router.post("/auth/login", response_model=TokenResponse, dependencies=[Depends(limiter.limit("5/minute"))])
async def login(payload: UserLoginRequest) -> TokenResponse:
    """
    Authenticate a merchant with phone + password.

    Returns a short‑lived JWT that must be passed as ``Authorization: Bearer <token>``
    on all protected endpoints.
    """
    try:
        token = await authenticate_user(payload.phone, payload.password)
        return token
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password",
        )


@router.get("/auth/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    """Return the profile of the currently authenticated merchant."""
    user = await get_user_by_id(current_user["user_id"])
    return UserResponse(
        id=user.id,
        name=user.name,
        phone=user.phone,
        whatsapp_connected=user.whatsapp_connected,
        plan=user.plan,
        created_at=user.created_at,
    )