#!/usr/bin/env bash
COOLIFY_BASE_URL="https://coolify-nexus-forge.freeddns.org"
COOLIFY_API_KEY="1|Qv8GbrjkxLiHeTEKVXqieyWnCq79i6v97sBO9N2431a0c09b"
APP_NAME="WhatsApp Order Auto-Wrangler"
REPO_URL="https://github.com/victoryphillips2475-ovrld/whatsapp-order-autowrangler.git"
BRANCH="main"
DOCKERFILE_PATH="/orderstream/Dockerfile"
PORT="8000"

# Create application (if not exists)
response=$(curl -s -X POST -H "Authorization: Bearer $COOLIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$APP_NAME\",\"git_repository\":\"$REPO_URL\",\"git_branch\":\"$BRANCH\",\"dockerfile_location\":\"$DOCKERFILE_PATH\",\"ports_exposes\":\"$PORT\"}" \
  "$COOLIFY_BASE_URL/api/v1/applications")

echo "Create response: $response"

# Extract app ID (jq)
APP_ID=$(echo "$response" | jq -r '.id // .uuid // .application_id // .id')
if [ -z "$APP_ID" ] || [ "$APP_ID" = "null" ]; then
  echo "Failed to get app ID. Check response."
  exit 1
fi

# Trigger deployment
deploy_resp=$(curl -s -X POST -H "Authorization: Bearer $COOLIFY_API_KEY" \
  "$COOLIFY_BASE_URL/api/v1/applications/${APP_ID}/deploy")

echo "Deploy response: $deploy_resp"
