#!/usr/bin/env python3
"""Utility script to create the required Appwrite collections, attributes,
indexes, and permissions for the OrderStream backend.

Run with ``python -m orderstream.backend.create_appwrite_collections`` or directly
``python3 create_appwrite_collections.py`` from the project root.
"""

import asyncio
from typing import List

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException

# Import project settings – validates required environment variables.
from orderstream.backend.config import settings

# ---------------------------------------------------------------------------
# Helper to initialise a ready‑to‑use Appwrite client.
# ---------------------------------------------------------------------------
def get_client() -> Client:
    client = Client()
    client.set_endpoint(settings.APPWRITE_ENDPOINT)
    client.set_project(settings.APPWRITE_PROJECT_ID)
    client.set_key(settings.APPWRITE_API_KEY)
    return client

# ---------------------------------------------------------------------------
# Generic permission set – any authenticated member may read/write.
# Adjust as needed for tighter security.
# ---------------------------------------------------------------------------
PERMISSIONS = [
    'read("role:member")',
    'write("role:member")',
]

# ---------------------------------------------------------------------------
# Collection creation – idempotent (ignores 409 conflict).
# ---------------------------------------------------------------------------
async def create_collection(db: Databases, collection_id: str, name: str) -> None:
    try:
        db.create_collection(
            database_id=settings.APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            name=name,
            permissions=PERMISSIONS,
            enabled=True,
        )
        print(f"[+] Collection '{collection_id}' created.")
    except AppwriteException as exc:
        if getattr(exc, "code", None) == 409:
            print(f"[=] Collection '{collection_id}' already exists – skipping.")
        else:
            raise

# ---------------------------------------------------------------------------
# Attribute helpers – each wrapper is idempotent.
# ---------------------------------------------------------------------------
async def create_string_attribute(
    db: Databases,
    collection_id: str,
    key: str,
    size: int,
    required: bool = True,
    default: str | None = None,
) -> None:
    try:
        db.create_string_attribute(
            database_id=settings.APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            key=key,
            size=size,
            required=required,
            default=default,
        )
        print(f"[+] String attribute '{key}' added to '{collection_id}'.")
    except AppwriteException as exc:
        if getattr(exc, "code", None) == 409:
            print(f"[=] String attribute '{key}' already exists on '{collection_id}'.")
        else:
            raise

async def create_boolean_attribute(
    db: Databases,
    collection_id: str,
    key: str,
    required: bool = True,
    default: bool | None = None,
) -> None:
    try:
        db.create_boolean_attribute(
            database_id=settings.APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            key=key,
            required=required,
            default=default,
        )
        print(f"[+] Boolean attribute '{key}' added to '{collection_id}'.")
    except AppwriteException as exc:
        if getattr(exc, "code", None) == 409:
            print(f"[=] Boolean attribute '{key}' already exists on '{collection_id}'.")
        else:
            raise

async def create_float_attribute(
    db: Databases,
    collection_id: str,
    key: str,
    required: bool = True,
    default: float | None = None,
) -> None:
    try:
        db.create_float_attribute(
            database_id=settings.APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            key=key,
            required=required,
            default=default,
        )
        print(f"[+] Float attribute '{key}' added to '{collection_id}'.")
    except AppwriteException as exc:
        if getattr(exc, "code", None) == 409:
            print(f"[=] Float attribute '{key}' already exists on '{collection_id}'.")
        else:
            raise

async def create_datetime_attribute(
    db: Databases,
    collection_id: str,
    key: str,
    required: bool = True,
    default: str | None = None,
) -> None:
    try:
        db.create_datetime_attribute(
            database_id=settings.APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            key=key,
            required=required,
            default=default,
        )
        print(f"[+] Datetime attribute '{key}' added to '{collection_id}'.")
    except AppwriteException as exc:
        if getattr(exc, "code", None) == 409:
            print(f"[=] Datetime attribute '{key}' already exists on '{collection_id}'.")
        else:
            raise

async def create_enum_attribute(
    db: Databases,
    collection_id: str,
    key: str,
    elements: List[str],
    required: bool = True,
    default: str | None = None,
) -> None:
    try:
        db.create_enum_attribute(
            database_id=settings.APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            key=key,
            elements=elements,
            required=required,
            default=default,
        )
        print(f"[+] Enum attribute '{key}' added to '{collection_id}'.")
    except AppwriteException as exc:
        if getattr(exc, "code", None) == 409:
            print(f"[=] Enum attribute '{key}' already exists on '{collection_id}'.")
        else:
            raise

# ---------------------------------------------------------------------------
# Index helper – creates a simple key index for the given attribute list.
# ---------------------------------------------------------------------------
async def create_key_index(
    db: Databases,
    collection_id: str,
    index_id: str,
    attributes: List[str],
) -> None:
    try:
        db.create_index(
            database_id=settings.APPWRITE_DATABASE_ID,
            collection_id=collection_id,
            key=index_id,
            attributes=attributes,
            type="key",
        )
        print(f"[+] Index '{index_id}' on {collection_id}({', '.join(attributes)}) created.")
    except AppwriteException as exc:
        if getattr(exc, "code", None) == 409:
            print(f"[=] Index '{index_id}' already exists on '{collection_id}'.")
        else:
            raise

# ---------------------------------------------------------------------------
# Main orchestration – creates both collections with their schema.
# ---------------------------------------------------------------------------
async def main() -> None:
    client = get_client()
    db = Databases(client)

    # ---------- Users collection ---------------------------------------
    await create_collection(db, "users", "Users")
    await create_string_attribute(db, "users", "name", size=100)
    await create_string_attribute(db, "users", "phone", size=20)
    await create_string_attribute(db, "users", "password_hash", size=255)
    await create_boolean_attribute(db, "users", "whatsapp_connected", required=True, default=False)
    await create_string_attribute(db, "users", "plan", size=20, required=True, default="basic")
    await create_datetime_attribute(db, "users", "created_at", required=True)
    # Index phone for quick lookup on login
    await create_key_index(db, "users", "phone_idx", ["phone"])

    # ---------- Orders collection --------------------------------------
    await create_collection(db, "orders", "Orders")
    await create_string_attribute(db, "orders", "customer_name", size=100)
    await create_string_attribute(db, "orders", "customer_phone", size=20)
    # Items are stored as a JSON string – large enough to hold typical payloads.
    await create_string_attribute(db, "orders", "items", size=65535)
    await create_float_attribute(db, "orders", "total")
    await create_enum_attribute(
        db,
        "orders",
        "status",
        elements=["pending", "confirmed", "fulfilled", "cancelled"],
        required=True,
        default="pending",
    )
    await create_datetime_attribute(db, "orders", "created_at", required=True)
    await create_string_attribute(db, "orders", "notes", size=500, required=False, default="")
    await create_string_attribute(db, "orders", "payment_link", size=255, required=False)
    # Indexes for common queries
    await create_key_index(db, "orders", "status_idx", ["status"])
    await create_key_index(db, "orders", "created_at_idx", ["created_at"])

    print("\nAll collections, attributes, and indexes are now ensured.")

if __name__ == "__main__":
    asyncio.run(main())
