# Rust Pattern — OVERLORD Empire Standard

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