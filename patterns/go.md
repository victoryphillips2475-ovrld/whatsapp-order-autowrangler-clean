# Go Pattern — OVERLORD Empire Standard

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