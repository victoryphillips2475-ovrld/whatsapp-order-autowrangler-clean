# Appwrite Pattern — OVERLORD Empire Standard

## SDK Version
```
appwrite==6.0.0
```

## Client Setup — Always from Environment
```python
import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.account import Account
from appwrite.services.storage import Storage
from appwrite.services.users import Users

def get_client() -> Client:
    client = Client()
    client.set_endpoint(os.environ["APPWRITE_ENDPOINT"])
    client.set_project(os.environ["APPWRITE_PROJECT_ID"])
    client.set_key(os.environ["APPWRITE_API_KEY"])
    return client

# Service helpers
def get_databases() -> Databases:
    return Databases(get_client())

def get_storage() -> Storage:
    return Storage(get_client())

def get_users() -> Users:
    return Users(get_client())
```

## Required .env Vars
```
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your_project_id
APPWRITE_API_KEY=your_api_key
APPWRITE_DATABASE_ID=your_database_id
```

## Database Operations
```python
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID

async def create_document(
    db: Databases,
    collection_id: str,
    data: dict,
    doc_id: str = None,
) -> dict:
    return db.create_document(
        database_id=os.environ["APPWRITE_DATABASE_ID"],
        collection_id=collection_id,
        document_id=doc_id or ID.unique(),
        data=data,
    )

async def get_document(db: Databases, collection_id: str, doc_id: str) -> dict:
    return db.get_document(
        database_id=os.environ["APPWRITE_DATABASE_ID"],
        collection_id=collection_id,
        document_id=doc_id,
    )

async def list_documents(
    db: Databases,
    collection_id: str,
    queries: list = None,
) -> dict:
    return db.list_documents(
        database_id=os.environ["APPWRITE_DATABASE_ID"],
        collection_id=collection_id,
        queries=queries or [],
    )

async def update_document(
    db: Databases,
    collection_id: str,
    doc_id: str,
    data: dict,
) -> dict:
    return db.update_document(
        database_id=os.environ["APPWRITE_DATABASE_ID"],
        collection_id=collection_id,
        document_id=doc_id,
        data=data,
    )

async def delete_document(
    db: Databases,
    collection_id: str,
    doc_id: str,
) -> None:
    db.delete_document(
        database_id=os.environ["APPWRITE_DATABASE_ID"],
        collection_id=collection_id,
        document_id=doc_id,
    )
```

## Query Patterns
```python
from appwrite.query import Query

# Common query patterns
queries = [
    Query.equal("status", "active"),
    Query.greater_than("created_at", "2024-01-01"),
    Query.order_desc("created_at"),
    Query.limit(25),
    Query.offset(0),
    Query.search("name", "search term"),
]
```

## Error Handling
```python
from appwrite.exception import AppwriteException

try:
    result = db.get_document(...)
except AppwriteException as e:
    if e.code == 404:
        raise ValueError(f"Document not found: {doc_id}")
    elif e.code == 401:
        raise PermissionError("Unauthorized Appwrite operation")
    else:
        raise Exception(f"Appwrite error {e.code}: {e.message}")
```

## Storage Operations
```python
from appwrite.input_file import InputFile

def upload_file(storage: Storage, bucket_id: str, file_path: str) -> dict:
    with open(file_path, "rb") as f:
        return storage.create_file(
            bucket_id=bucket_id,
            file_id=ID.unique(),
            file=InputFile.from_bytes(f.read(), filename=os.path.basename(file_path)),
        )

def get_file_url(bucket_id: str, file_id: str) -> str:
    endpoint = os.environ["APPWRITE_ENDPOINT"]
    project = os.environ["APPWRITE_PROJECT_ID"]
    return f"{endpoint}/storage/buckets/{bucket_id}/files/{file_id}/view?project={project}"
```

## NEVER
- Never use raw HTTP to Appwrite — SDK only
- Never hardcode endpoint, project ID, or API key
- Never catch bare Exception without re-raising or logging
- Never assume a document exists — always handle AppwriteException code 404