# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/models/users.py
"""User/merchant Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator
import re


class UserRegisterRequest(BaseModel):
    """Payload for new merchant registration."""

    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=7, max_length=20)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        return re.sub(r"(?!^\+)[^\d]", "", v)  # strip non-digits except leading +

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", v):
            raise ValueError("Password must contain at least one special character (!@#$%^&*...)")
        return v


class UserLoginRequest(BaseModel):
    """Payload for merchant login."""

    phone: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    """Public merchant profile (no password hash exposed)."""

    id: str
    name: str
    phone: str
    whatsapp_connected: bool = False
    plan: str = "basic"
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT token returned on successful login."""

    access_token: str = Field(readonly=True)
    token_type: str = "bearer"
    expires_in: int  # seconds