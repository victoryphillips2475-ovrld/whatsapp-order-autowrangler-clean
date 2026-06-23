# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/services/auth_service.py
"""Authentication service — handles user registration and login via Appwrite.

The Appwrite Python SDK is synchronous, so all blocking calls run inside
``run_in_threadpool`` to keep FastAPI endpoints fully async.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Optional

from fastapi.concurrency import run_in_threadpool
from passlib.hash import bcrypt as _pwd_hash

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException

from ..config import settings
from ..dependencies import create_access_token
from ..models.users import UserRegisterRequest, UserResponse, TokenResponse

_logger = logging.getLogger("uvicorn.error")

# ---------------------------------------------------------------------------
# SDK initialisation (shared with order_service — fine because Client is stateless)
# ---------------------------------------------------------------------------
_client = Client()
_client.set_endpoint(settings.APPWRITE_ENDPOINT)
_client.set_project(settings.APPWRITE_PROJECT_ID)
_client.set_key(settings.APPWRITE_API_KEY)
_db = Databases(_client)
_USERS_COLLECTION = "users"


def _normalize_phone(phone: str) -> str:
    return re.sub(r"(?!^\+)[^\d]", "", phone)


# ---------------------------------------------------------------------------
# Sync helpers (run in thread pool)
# ---------------------------------------------------------------------------
def _list_users_sync(phone: str) -> list[dict]:
    from appwrite.query import Query

    return _db.list_documents(
        settings.APPWRITE_DATABASE_ID,
        _USERS_COLLECTION,
        queries=[Query.equal("phone", _normalize_phone(phone)), Query.limit(1)],
    ).get("documents", [])


def _create_user_sync(name: str, phone: str, password_hash: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return _db.create_document(
        settings.APPWRITE_DATABASE_ID,
        _USERS_COLLECTION,
        id="unique()",
        data={
            "name": name,
            "phone": _normalize_phone(phone),
            "password_hash": password_hash,
            "whatsapp_connected": False,
            "plan": "basic",
            "created_at": now,
        },
    )


def _get_user_by_id_sync(user_id: str) -> dict:
    return _db.get_document(settings.APPWRITE_DATABASE_ID, _USERS_COLLECTION, user_id)


def _verify_password(plain: str, hashed: str) -> bool:
    return _pwd_hash.verify(plain, hashed)


# ---------------------------------------------------------------------------
# Public async API
# ---------------------------------------------------------------------------
async def get_user_by_id(user_id: str) -> UserResponse:
    """Fetch a user document by ID and return a UserResponse."""
    try:
        doc = await run_in_threadpool(_get_user_by_id_sync, user_id)
    except AppwriteException as exc:
        if exc.code == 404:
            raise FileNotFoundError(f"User {user_id} not found")
        raise
    return UserResponse(
        id=doc["$id"],
        name=doc.get("name", ""),
        phone=doc.get("phone", ""),
        whatsapp_connected=doc.get("whatsapp_connected", False),
        plan=doc.get("plan", "basic"),
        created_at=datetime.fromisoformat(doc["created_at"]).replace(tzinfo=timezone.utc),
    )


async def register_user(payload: UserRegisterRequest) -> UserResponse:
    """
    Register a new merchant.

    Raises:
        ValueError: If the phone number is already registered.
        AppwriteException: On database errors.
    """
    phone = _normalize_phone(payload.phone)

    # Check for existing user
    existing = await run_in_threadpool(_list_users_sync, phone)
    if existing:
        raise ValueError(f"Phone number {phone} is already registered")

    password_hash = _pwd_hash.hash(payload.password)

    try:
        doc = await run_in_threadpool(_create_user_sync, payload.name, phone, password_hash)
    except AppwriteException as exc:
        # Appwrite unique-constraint violation (race: two concurrent registrations)
        if exc.code == 409:
            raise ValueError(f"Phone number {phone} is already registered")
        _logger.error("Appwrite create_document failed during registration: %s", exc)
        raise

    return UserResponse(
        id=doc["$id"],
        name=doc["name"],
        phone=doc["phone"],
        whatsapp_connected=doc.get("whatsapp_connected", False),
        plan=doc.get("plan", "basic"),
        created_at=datetime.fromisoformat(doc["created_at"]).replace(tzinfo=timezone.utc),
    )


async def authenticate_user(phone: str, password: str) -> TokenResponse:
    """
    Authenticate a merchant by phone + password and return a JWT.

    Raises:
        ValueError: If credentials are invalid.
    """
    phone = _normalize_phone(phone)

    docs = await run_in_threadpool(_list_users_sync, phone)
    if not docs:
        raise ValueError("Invalid phone or password")

    doc = docs[0]
    if not _verify_password(password, doc.get("password_hash", "")):
        raise ValueError("Invalid phone or password")

    token = create_access_token(data={"sub": doc["$id"]})
    return TokenResponse(
        access_token=token,
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
    )