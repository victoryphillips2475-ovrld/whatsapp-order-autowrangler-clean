# CODEX — VULCAN Reference

See Kilo config for full prompt. This file is a pipeline position reference.

## What CODEX Is
CODEX is the legal documentation agent. It writes Terms of Service, Privacy Policy, Refund Policy, and Cookie Policy for each product. CODEX runs in parallel with SCRIBE after the build plan is confirmed, and flags high‑risk products for CIPHER review.

## Pipeline Position
BLUEPRINT → LOOM → VULCAN → CODEX → LOOM → ALCHEMIST → RAZE → MORPH → WEAVE → SENTINEL → JANUS → SCRIBE

## Memory Bank Paths
- .kairos/memory/project-context.md   — product context (read on startup)
- .kairos/memory/in-progress.md       — tracks document creation status
- .kairos/memory/vulcan-decisions.md  — legal‑related decisions
