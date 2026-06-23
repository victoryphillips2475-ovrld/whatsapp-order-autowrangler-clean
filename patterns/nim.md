# NIM Inference Pattern — OVERLORD Empire Standard

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