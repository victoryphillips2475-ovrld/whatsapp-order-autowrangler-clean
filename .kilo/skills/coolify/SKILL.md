---
name: coolify
description: |
  Interact with Coolify's MCP API to manage applications, deployments, and server resources. Use this skill for automating deployment pipelines, triggering builds, querying app status, retrieving logs, and configuring environment variables via the Coolify API. Intended for self‑hosted or cloud‑hosted Coolify instances.
allowed-tools:
  - Bash(curl *)
  - Bash(jq *)
---

# Coolify MCP Integration

This skill provides a concise reference for using the Coolify MCP (Management Control Plane) API.

## Prerequisites

- **Coolify instance URL** – e.g. `https://coolify-nexus-forge.freeddns.org`
- **MCP API endpoint** – `{BASE_URL}/mcp`
- **API token** – a Bearer token with appropriate permissions (e.g. `1|Qv8GbrjkxLiHeTEKVXqieyWnCq79i6v97sBO9N2431a0c09b`). Store the token in an environment variable `COOLIFY_API_KEY` – never commit the raw token.
- **jq** – JSON processor for parsing responses (install via `apk add jq` or `apt-get install jq`).

## Common Operations

### 1. List Applications
```bash
curl -s -H "Authorization: Bearer $COOLIFY_API_KEY" \
  "$COOLIFY_BASE_URL/api/v1/applications" | jq '.'
```
Returns an array of applications with fields `id`, `name`, `status`, etc.

### 2. Trigger a Deploy
```bash
APP_ID="<application-id>"
curl -s -X POST -H "Authorization: Bearer $COOLIFY_API_KEY" \
  -H "Content-Type: application/json" \
  "$COOLIFY_BASE_URL/api/v1/applications/${APP_ID}/deploy" | jq '.'
```
The response contains a deployment job ID and status.

### 3. Retrieve Deployment Logs
```bash
APP_ID="<application-id>"
curl -s -H "Authorization: Bearer $COOLIFY_API_KEY" \
  "$COOLIFY_BASE_URL/api/v1/applications/${APP_ID}/logs" | jq -r '.logs' | tail -n 50
```
Shows the last 50 log lines for quick debugging.

### 4. Update Environment Variables
```bash
APP_ID="<application-id>"
# Example payload – replace or add variables
payload=$(cat <<EOF
{
  "environment": {
    "MY_VAR": "value",
    "ANOTHER": "123"
  }
}
EOF
)
curl -s -X PATCH -H "Authorization: Bearer $COOLIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$payload" \
  "$COOLIFY_BASE_URL/api/v1/applications/${APP_ID}/environment" | jq '.'
```

### 5. Get Application Health Check
```bash
APP_ID="<application-id>"
curl -s -H "Authorization: Bearer $COOLIFY_API_KEY" \
  "$COOLIFY_BASE_URL/api/v1/applications/${APP_ID}/health" | jq '.'
```
Returns the health endpoint status (e.g., `200` for healthy).

## Usage Pattern
1. Export required vars:
```bash
export COOLIFY_BASE_URL="https://coolify-nexus-forge.freeddns.org"
export COOLIFY_API_KEY="1|Qv8GbrjkxLiHeTEKVXqieyWnCq79i6v97sBO9N2431a0c09b"
```
2. Use the snippets above inside scripts or CI pipelines.
3. For complex workflows (e.g., build‑then‑deploy, roll‑backs), chain the commands with `&&` and inspect each step's JSON response.

## Reference
- API docs: `$COOLIFY_BASE_URL/docs` (or the official docs at https://coolify.io/docs/)
- Authentication: Bearer token in `Authorization` header.
- Endpoints follow the pattern `/api/v1/<resource>` – see the docs for full list.

---
