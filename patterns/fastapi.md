# FastAPI Pattern — OVERLORD Empire Standard

## Project Structure
```
project/
├── main.py           ← app entry point, lifespan, middleware
├── routers/
│   └── {domain}.py   ← one file per domain (users, products, etc.)
├── models/
│   └── {domain}.py   ← Pydantic request/response models
├── services/
│   └── {domain}.py   ← business logic, no FastAPI imports here
├── dependencies.py   ← shared Depends() functions (auth, db)
├── config.py         ← settings from env vars via pydantic-settings
└── requirements.txt
```

## App Entry Point
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, products

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown

app = FastAPI(title="Product Name", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ["CORS_ORIGINS"].split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(products.router, prefix="/products", tags=["products"])

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
```

## Pydantic Models — Always First
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class CreateUserRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        return v.lower()

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime

class ErrorResponse(BaseModel):
    detail: str
    code: str
```

## Route Handler Pattern
```python
from fastapi import APIRouter, HTTPException, Depends, status
from models.users import CreateUserRequest, UserResponse, ErrorResponse
from services.users import UserService
from dependencies import get_current_user

router = APIRouter()

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
async def create_user(
    payload: CreateUserRequest,
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    try:
        user = await UserService.create(payload)
        return UserResponse(**user)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error")
```

## Service Layer — No FastAPI Imports
```python
# services/users.py
import httpx
from models.users import CreateUserRequest, UserResponse

class UserService:
    @staticmethod
    async def create(payload: CreateUserRequest) -> dict:
        # business logic here
        # raise ValueError for business rule violations
        # raise Exception for unexpected errors
        pass
```

## Config from Environment
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    appwrite_endpoint: str
    appwrite_project_id: str
    appwrite_api_key: str
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

settings = Settings()
```

## Async HTTP Calls — Always httpx
```python
import httpx

async def call_external(url: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {os.environ['API_KEY']}"},
        )
        response.raise_for_status()
        return response.json()
```

## Error Handling Rules
- ValueError → 400 or 409 (business rule violation)
- PermissionError → 403
- FileNotFoundError → 404
- httpx.HTTPStatusError → forward status or 502
- Exception → 500 with generic message (never expose internals)
- Always: specific exception type, never bare except

## Requirements Format
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0
pydantic-settings==2.6.0
httpx==0.27.0
python-dotenv==1.0.1
```

## Run Command (VPS)
```bash
/opt/overlord/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```