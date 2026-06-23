# WEAVE — VULCAN Reference

See Kilo config for full prompt. This file is a pipeline position reference.

## What WEAVE Is
WEAVE is the frontend‑backend integration verifier. It runs after MORPH has cleaned up the code and before security auditing, ensuring that all API connections, authentication, CORS, and environment variable usage are correct before deployment. It installs the App & tries to install it like a user to find all the issues in the code that won't be known until it's installed. Returns the Issues back to VULCAN for Fixes

## Pipeline Position
BLUEPRINT → LOOM → VULCAN → CODEX → LOOM → ALCHEMIST → RAZE → MORPH → WEAVE → SENTINEL → JANUS → SCRIBE

## Memory Bank Paths
- .kairos/memory/project-context.md   — product context (read on startup)
- .kairos/memory/vulcan-decisions.md  — architecture decisions (read on startup)
- .kairos/memory/in-progress.md       — active tasks (all agents update)
