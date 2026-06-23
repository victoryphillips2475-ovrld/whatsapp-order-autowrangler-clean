# n8n Pattern — OVERLORD Empire Standard

## Webhook Base
```
http://localhost:5678/webhook/
```

## Trigger n8n Workflow
```python
import httpx
import os

async def trigger_n8n(webhook_path: str, payload: dict) -> dict:
    """
    Trigger an n8n webhook workflow.
    webhook_path: the path segment after /webhook/ (e.g. 'kairos/lead-qualified')
    """
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
    """Non-blocking trigger — does not wait for workflow completion."""
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