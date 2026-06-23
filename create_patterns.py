#!/usr/bin/env python3
"""
OVERLORD — VULCAN Pattern Files + Supporting Templates
Creates: patterns/, .kairos/templates/, scripts/
Run from: /home/overlord/.openclaw/workspace/VULCAN/
"""

import os

VULCAN_BASE = '/home/overlord/.openclaw/workspace/VULCAN'
PATTERNS = f'{VULCAN_BASE}/patterns'
TEMPLATES = f'{VULCAN_BASE}/.kairos/templates'
SCRIPTS = f'{VULCAN_BASE}/scripts'

os.makedirs(PATTERNS, exist_ok=True)
os.makedirs(TEMPLATES, exist_ok=True)
os.makedirs(SCRIPTS, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
FASTAPI = """# FastAPI Pattern — OVERLORD Empire Standard

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
"""

# ─────────────────────────────────────────────────────────────────────────────
APPWRITE = """# Appwrite Pattern — OVERLORD Empire Standard

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
"""

# ─────────────────────────────────────────────────────────────────────────────
NIM = """# NIM Inference Pattern — OVERLORD Empire Standard

## API Base
```
https://integrate.api.nvidia.com/v1
```

## Required Env Var
```
NIM_API_KEY=nvapi-...
```

## Standard Inference Call
```python
import httpx
import os

async def nim_complete(
    model: str,
    messages: list[dict],
    max_tokens: int = 2048,
    temperature: float = 0.7,
) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['NIM_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
```

## Key Rotation on Rate Limit
```python
import os
import httpx

NIM_KEYS = [k.strip() for k in os.environ.get("NIM_API_KEYS", os.environ.get("NIM_API_KEY", "")).split(",") if k.strip()]
_key_index = 0

def get_nim_key() -> str:
    global _key_index
    key = NIM_KEYS[_key_index % len(NIM_KEYS)]
    return key

def rotate_nim_key():
    global _key_index
    _key_index += 1

async def nim_complete_with_rotation(model: str, messages: list[dict], max_tokens: int = 2048) -> str:
    for attempt in range(len(NIM_KEYS)):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {get_nim_key()}"},
                    json={"model": model, "messages": messages, "max_tokens": max_tokens},
                )
                if response.status_code in (401, 403, 429):
                    rotate_nim_key()
                    continue
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError:
            rotate_nim_key()
    raise Exception("All NIM keys exhausted or rate-limited")
```

## Model Tier Reference
```
Fast     : meta/llama-3.1-8b-instruct          (131K ctx)
Large    : meta/llama-3.3-70b-instruct          (131K ctx)
Smart    : nvidia/nemotron-3-super-120b-a12b    (128K ctx)
Coder    : minimaxai/minimax-m2.7               (200K ctx)
Deep     : deepseek-ai/deepseek-r1              (131K ctx)
Write    : mistralai/mixtral-8x22b-instruct     (65K ctx)
```

## System Message Pattern
```python
messages = [
    {"role": "system", "content": "You are a specialist in..."},
    {"role": "user", "content": user_prompt},
]
```

## NEVER
- Never use Groq as inference provider
- Never use OpenAI SDK (use httpx directly)
- Never hardcode NIM_API_KEY in source
- Never set timeout below 60s for large models
"""

# ─────────────────────────────────────────────────────────────────────────────
N8N = """# n8n Pattern — OVERLORD Empire Standard

## Webhook Base
```
http://localhost:5678/webhook/
```

## Trigger n8n Workflow
```python
import httpx
import os

async def trigger_n8n(webhook_path: str, payload: dict) -> dict:
    \"\"\"
    Trigger an n8n webhook workflow.
    webhook_path: the path segment after /webhook/ (e.g. 'kairos/lead-qualified')
    \"\"\"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"http://localhost:5678/webhook/{webhook_path}",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json() if response.text else {}
```

## Fire-and-Forget (no response needed)
```python
async def trigger_n8n_async(webhook_path: str, payload: dict) -> None:
    \"\"\"Non-blocking trigger — does not wait for workflow completion.\"\"\"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f"http://localhost:5678/webhook/{webhook_path}",
                json=payload,
            )
    except Exception:
        pass  # fire-and-forget: log but never block main flow
```

## Standard Payload Shape
```python
payload = {
    "event": "lead.qualified",          # event type
    "source": "QUALIFIER",              # sending agent
    "timestamp": datetime.utcnow().isoformat(),
    "data": {                           # event-specific data
        "lead_id": "...",
        "score": 85,
    },
}
```

## Error Handling
```python
from httpx import ConnectError, TimeoutException

try:
    result = await trigger_n8n("kairos/lead-qualified", payload)
except ConnectError:
    # n8n is not running — log and continue, do not crash main flow
    pass
except TimeoutException:
    # workflow is slow — acceptable for fire-and-forget
    pass
```

## NEVER
- Never use requests library — async httpx only
- Never block main application flow waiting for n8n response
- Never hardcode webhook paths — define as constants or config
- Never send sensitive data (API keys, passwords) in webhook payloads
"""

# ─────────────────────────────────────────────────────────────────────────────
OPENCLAW = """# OpenClaw Pattern — OVERLORD Empire Standard

## Config Location
```
/home/overlord/.openclaw/openclaw.json
```

## Agent Workspace Structure
```
/home/overlord/.openclaw/workspace/{AGENT_NAME}/
├── SOUL.md        ← behavioral spec (primary system prompt)
├── IDENTITY.md    ← role card
├── PERSONA.md     ← Victory's voice (shared across all agents)
├── TOOLS.md       ← infrastructure manifest
├── AGENTS.md      ← workspace rules + agent-specific red lines
├── MEMORY.md      ← long-term memory
├── DREAMS.md      ← aspirational context
├── HEARTBEAT.md   ← proactive task checklist
├── USER.md        ← Victory's profile
└── memory/
    └── YYYY-MM-DD.md  ← daily session logs
```

## Adding Agent to openclaw.json
```python
import json

with open('/home/overlord/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

new_agent = {
    "id": "agent_name_lowercase",
    "model": {
        "primary": "nim/meta/llama-3.3-70b-instruct"
    },
    "workspace": "/home/overlord/.openclaw/workspace/AGENT_NAME"
}

# Check for duplicates before appending
existing_ids = [a.get('id') for a in config['agents']['list']]
if new_agent['id'] not in existing_ids:
    config['agents']['list'].append(new_agent)

with open('/home/overlord/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)
```

## Model Tier Assignment
```
Fast agents (HOOK, HANDLER):     nim/meta/llama-3.1-8b-instruct
Large agents (RETAINER, HERMES): nim/meta/llama-3.3-70b-instruct
Smart agents (SPECTRAL, ORACLE): nim/nvidia/nemotron-3-super-120b-a12b
Deep agents (CLOSER, ARCHITECT): nim/deepseek-ai/deepseek-r1
Coder agents (VULCAN):           nim/minimaxai/minimax-m2.7
```

## SOUL.md Required Sections
```
# AGENT_NAME — SOUL FILE
## IDENTITY
## THE HUMANIZER
## [AGENT-SPECIFIC COVENANT / RULES]
## [AGENT] NEVER
## [AGENT] ALWAYS
## [AGENT] ROUTING LOGIC
## HARD OVERRIDES — FINAL AUTHORITY
## MEMORY RULES
```

## NEVER
- Never modify openclaw.json without explicit instruction from Your Majesty
- Never edit another agent's SOUL.md or MEMORY.md
- Never add an agent without checking for existing ID conflicts
- Never use system python — always /opt/overlord/venv/bin/python3 for scripts
"""

# ─────────────────────────────────────────────────────────────────────────────
GO = """# Go Pattern — OVERLORD Empire Standard

## Project Structure
```
project/
├── cmd/
│   └── main.go          ← entry point
├── internal/
│   ├── handlers/        ← HTTP handlers
│   ├── services/        ← business logic
│   ├── models/          ← structs and types
│   └── middleware/      ← auth, logging, etc.
├── config/
│   └── config.go        ← env var loading
├── go.mod
└── go.sum
```

## Gin API Entry Point
```go
package main

import (
    "log"
    "os"
    "github.com/gin-gonic/gin"
    "github.com/joho/godotenv"
    "project/internal/handlers"
    "project/internal/middleware"
)

func main() {
    godotenv.Load()

    r := gin.Default()
    r.Use(middleware.CORS())

    r.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{"status": "ok"})
    })

    api := r.Group("/api/v1")
    api.Use(middleware.Auth())
    {
        api.GET("/users/:id", handlers.GetUser)
        api.POST("/users", handlers.CreateUser)
    }

    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }
    log.Fatal(r.Run(":" + port))
}
```

## Handler Pattern
```go
package handlers

import (
    "net/http"
    "github.com/gin-gonic/gin"
    "project/internal/services"
    "project/internal/models"
)

func CreateUser(c *gin.Context) {
    var req models.CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    user, err := services.CreateUser(c.Request.Context(), req)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
        return
    }

    c.JSON(http.StatusCreated, user)
}
```

## Service Pattern
```go
package services

import (
    "context"
    "fmt"
    "project/internal/models"
)

func CreateUser(ctx context.Context, req models.CreateUserRequest) (*models.User, error) {
    // business logic here
    // return nil, fmt.Errorf("user already exists: %s", req.Email)
    return &models.User{}, nil
}
```

## Struct Patterns
```go
package models

type CreateUserRequest struct {
    Email string `json:"email" binding:"required,email"`
    Name  string `json:"name" binding:"required,min=1,max=100"`
}

type User struct {
    ID        string `json:"id"`
    Email     string `json:"email"`
    Name      string `json:"name"`
    CreatedAt string `json:"created_at"`
}
```

## HTTP Client (no default client)
```go
import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "time"
)

var httpClient = &http.Client{Timeout: 30 * time.Second}

func callExternal(url string, payload any) ([]byte, error) {
    body, _ := json.Marshal(payload)
    req, err := http.NewRequest("POST", url, bytes.NewBuffer(body))
    if err != nil {
        return nil, fmt.Errorf("request creation failed: %w", err)
    }
    req.Header.Set("Content-Type", "application/json")
    resp, err := httpClient.Do(req)
    if err != nil {
        return nil, fmt.Errorf("request failed: %w", err)
    }
    defer resp.Body.Close()
    // read and return body
    return nil, nil
}
```

## go.mod Format
```
module github.com/kairos/{project}

go 1.22

require (
    github.com/gin-gonic/gin v1.10.0
    github.com/joho/godotenv v1.5.1
)
```

## NEVER
- Never use http.DefaultClient (no timeout)
- Never ignore error return values — always handle
- Never launch goroutines without cancellation context
- Never panic in handlers — return errors as JSON
"""

# ─────────────────────────────────────────────────────────────────────────────
RUST = """# Rust Pattern — OVERLORD Empire Standard

## Project Structure
```
project/
├── src/
│   ├── main.rs          ← entry point
│   ├── handlers/        ← HTTP handlers
│   ├── services/        ← business logic
│   ├── models/          ← structs, serde derives
│   ├── errors.rs        ← custom error types
│   └── config.rs        ← env var loading
├── Cargo.toml
└── .env
```

## Cargo.toml
```toml
[package]
name = "project"
version = "0.1.0"
edition = "2021"

[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
reqwest = { version = "0.12", features = ["json"] }
dotenvy = "0.15"
thiserror = "1"
```

## Axum Entry Point
```rust
use axum::{routing::{get, post}, Router};
use std::net::SocketAddr;

#[tokio::main]
async fn main() {
    dotenvy::dotenv().ok();

    let app = Router::new()
        .route("/health", get(health))
        .route("/users", post(handlers::create_user))
        .route("/users/:id", get(handlers::get_user));

    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn health() -> &'static str { "ok" }
```

## Models — Always Derive serde
```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
pub struct CreateUserRequest {
    pub email: String,
    pub name: String,
}

#[derive(Debug, Serialize)]
pub struct UserResponse {
    pub id: String,
    pub email: String,
    pub name: String,
}
```

## Error Handling — thiserror, Never unwrap() in Handlers
```rust
use thiserror::Error;
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use axum::Json;
use serde_json::json;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Not found: {0}")]
    NotFound(String),
    #[error("Validation error: {0}")]
    Validation(String),
    #[error("Internal error")]
    Internal(#[from] anyhow::Error),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, message) = match self {
            AppError::NotFound(msg) => (StatusCode::NOT_FOUND, msg),
            AppError::Validation(msg) => (StatusCode::BAD_REQUEST, msg),
            AppError::Internal(_) => (StatusCode::INTERNAL_SERVER_ERROR, "Internal error".into()),
        };
        (status, Json(json!({"error": message}))).into_response()
    }
}
```

## Handler Pattern
```rust
use axum::{extract::Path, Json};
use crate::{errors::AppError, models::{CreateUserRequest, UserResponse}};

pub async fn create_user(
    Json(payload): Json<CreateUserRequest>,
) -> Result<Json<UserResponse>, AppError> {
    // never use .unwrap() here
    let user = services::create_user(payload).await
        .map_err(|e| AppError::Internal(e.into()))?;
    Ok(Json(user))
}
```

## Async HTTP (reqwest)
```rust
use reqwest::Client;
use std::time::Duration;

async fn call_external(url: &str, payload: &serde_json::Value) -> anyhow::Result<serde_json::Value> {
    let client = Client::builder()
        .timeout(Duration::from_secs(30))
        .build()?;

    let response = client
        .post(url)
        .json(payload)
        .send()
        .await?
        .error_for_status()?
        .json::<serde_json::Value>()
        .await?;

    Ok(response)
}
```

## NEVER
- Never use .unwrap() or .expect() in production handlers
- Never use blocking operations inside async functions (use tokio::task::spawn_blocking)
- Never ignore Result — always propagate with ? or handle explicitly
"""

# ─────────────────────────────────────────────────────────────────────────────
TYPESCRIPT = """# TypeScript + Hono Pattern — OVERLORD Empire Standard

## Project Structure
```
project/
├── src/
│   ├── index.ts         ← app entry point
│   ├── routes/
│   │   └── users.ts     ← one file per domain
│   ├── services/
│   │   └── users.ts     ← business logic
│   ├── models/
│   │   └── users.ts     ← Zod schemas + TypeScript types
│   └── middleware/
│       └── auth.ts      ← auth middleware
├── package.json
├── tsconfig.json
└── .env
```

## package.json
```json
{
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "hono": "^4.6.0",
    "@hono/node-server": "^1.13.0",
    "zod": "^3.23.0",
    "dotenv": "^16.4.0"
  },
  "devDependencies": {
    "typescript": "^5.6.0",
    "tsx": "^4.19.0",
    "@types/node": "^22.0.0"
  }
}
```

## Hono Entry Point
```typescript
import { serve } from '@hono/node-server'
import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { usersRouter } from './routes/users'

const app = new Hono()

app.use('*', logger())
app.use('*', cors({
  origin: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
}))

app.get('/health', (c) => c.json({ status: 'ok' }))
app.route('/users', usersRouter)

serve({ fetch: app.fetch, port: Number(process.env.PORT) || 3000 })
```

## Models — Zod First
```typescript
import { z } from 'zod'

export const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
})

export const UserResponseSchema = z.object({
  id: z.string(),
  email: z.string(),
  name: z.string(),
  createdAt: z.string().datetime(),
})

export type CreateUserInput = z.infer<typeof CreateUserSchema>
export type UserResponse = z.infer<typeof UserResponseSchema>
```

## Route Pattern
```typescript
import { Hono } from 'hono'
import { zValidator } from '@hono/zod-validator'
import { CreateUserSchema } from '../models/users'
import { UserService } from '../services/users'

export const usersRouter = new Hono()

usersRouter.post('/', zValidator('json', CreateUserSchema), async (c) => {
  const payload = c.req.valid('json')
  try {
    const user = await UserService.create(payload)
    return c.json(user, 201)
  } catch (err) {
    if (err instanceof Error && err.message.includes('already exists')) {
      return c.json({ error: err.message }, 409)
    }
    return c.json({ error: 'Internal error' }, 500)
  }
})
```

## Async HTTP — fetch with AbortSignal
```typescript
async function callExternal(url: string, payload: unknown): Promise<unknown> {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.API_KEY}`,
    },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(30_000),
  })

  if (!response.ok) {
    throw new Error(`External call failed: ${response.status}`)
  }

  return response.json()
}
```

## tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "strict": true,
    "noImplicitAny": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
```

## NEVER
- Never use any type — define proper interfaces or use unknown
- Never use fetch() without AbortSignal.timeout()
- Never use var — const or let only
- Never suppress TypeScript errors with @ts-ignore unless absolutely necessary
"""

# ─────────────────────────────────────────────────────────────────────────────
DEEP_WEB_SEARCH = """# Deep Web Search Architecture — OVERLORD Empire Standard

## When to Use This Pattern
- Before writing code that uses an unfamiliar API or library
- When verifying current package versions before pinning them
- When researching a technical approach before implementing
- When debugging requires understanding an error pattern

## The 4-Phase Pipeline

### PHASE 1 — Intent Parsing & Query Generation
Never pass raw questions to a search engine. Generate 3-5 parallel sub-queries.

Example:
  Task: "Find the current stable version of httpx"
  Queries:
    - "httpx python package latest stable version 2025"
    - "httpx pypi release history"
    - "site:pypi.org httpx"

### PHASE 2 — Retrieval (Wide Net)
Use Tavily for semantic search (primary):
```python
import httpx, os

async def tavily_search(query: str, max_results: int = 5) -> list[dict]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": os.environ["TAVILY_API_KEY"],
                "query": query,
                "max_results": max_results,
                "include_raw_content": False,
            }
        )
        response.raise_for_status()
        return response.json().get("results", [])
```

Use Firecrawl for full page extraction (when URL is known):
```python
async def firecrawl_fetch(url: str) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {os.environ['FIRECRAWL_API_KEY']}"},
            json={"url": url, "formats": ["markdown"]}
        )
        response.raise_for_status()
        return response.json().get("data", {}).get("markdown", "")
```

SearXNG as fallback:
```python
async def searxng_search(query: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            "http://localhost:8888/search",
            params={"q": query, "format": "json", "categories": "general"}
        )
        return response.json().get("results", [])
```

### PHASE 3 — Extraction & Ranking
- From search results, collect the top 5-10 URLs
- Fetch the most promising 2-3 with Firecrawl
- Extract only the relevant sections (not entire pages)
- Prioritize: official docs > package registry > trusted blogs > forums

### PHASE 4 — Grounding & Use
- State the source for any fact you act on
- For package versions: verify on pypi.org, npmjs.com, or crates.io directly
- For API patterns: verify against official documentation URL
- Never act on a single source for version-critical information

## Quick Pattern for Package Version Check
```python
async def get_latest_pypi_version(package: str) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"https://pypi.org/pypi/{package}/json")
        response.raise_for_status()
        return response.json()["info"]["version"]
```

## RULES
1. Never send raw user prompts to search — decompose first
2. Use Tavily for conceptual queries, Firecrawl for known URLs
3. Cross-reference at least 2 sources for version pinning
4. SearXNG (localhost:8888) is fallback only — not primary
5. Include date in queries for time-sensitive information
"""

# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT.MD TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────
PRODUCT_MD_TEMPLATE = """# {PRODUCT_NAME} — Product.md
**Status:** PLANNING
**Stack:** {LANGUAGE} / {FRAMEWORK}
**Gumroad URL:** —
**Last Updated:** {DATE}

---

## What It Does
{ONE_PARAGRAPH_DESCRIPTION}

## Target User
{WHO_THIS_IS_FOR}

## File Structure
```
{DIRECTORY_TREE}
```

## Implemented
<!-- VULCAN updates this after each session -->

## Pending (Post-Ship)
<!-- Items from BUILD PLAN not in MVP scope -->

## Known Issues
<!-- RAZE conditional warnings, JANUS degraded flags -->

## Environment Variables
| Variable | Purpose | Example |
|---|---|---|
| | | |

## Deployment
- GitHub repo: —
- Coolify app ID: —
- Live URL: —

## Legal
- Terms of Service: docs/legal/terms-of-service.md
- Privacy Policy: docs/legal/privacy-policy.md
- Refund Policy: docs/legal/refund-policy.md

## Changelog
<!-- VULCAN appends one line per session: [DATE] what changed -->
"""

# ─────────────────────────────────────────────────────────────────────────────
# WRITE ALL FILES
# ─────────────────────────────────────────────────────────────────────────────

files = {
    f'{PATTERNS}/fastapi.md': FASTAPI,
    f'{PATTERNS}/appwrite.md': APPWRITE,
    f'{PATTERNS}/nim.md': NIM,
    f'{PATTERNS}/n8n.md': N8N,
    f'{PATTERNS}/openclaw.md': OPENCLAW,
    f'{PATTERNS}/go.md': GO,
    f'{PATTERNS}/rust.md': RUST,
    f'{PATTERNS}/typescript.md': TYPESCRIPT,
    f'{PATTERNS}/deep-web-search-architecture.md': DEEP_WEB_SEARCH,
    f'{TEMPLATES}/product-md-template.md': PRODUCT_MD_TEMPLATE,
}

print('=' * 60)
print('VULCAN PATTERN FILES + TEMPLATES')
print('=' * 60)

for path, content in files.items():
    with open(path, 'w') as f:
        f.write(content.strip())
    print(f'  WROTE  {path.replace(VULCAN_BASE, "")} ({len(content):,} chars)')

# Remind about deep-web-search skill copy
print()
print('NOTE: Copy your uploaded deep-web-search skill over the pattern file:')
print(f'  cp /path/to/deep-web-search-architecture-skill.md \\')
print(f'     {PATTERNS}/deep-web-search-architecture.md')
print()
print(f'Pattern files: {PATTERNS}/')
print(f'Templates: {TEMPLATES}/')
print()
print('VULCAN Pattern Protocol is now complete.')
print('All agents in pipeline are live and pattern-aware.')
