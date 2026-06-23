# JANUS — VULCAN Reference

See Kilo config for full prompt. This file is a pipeline position reference.

## What JANUS Is
JANUS is the launch and deployment agent. It creates Dockerfiles or docker‑compose files if missing, pushes the repository to GitHub, triggers a Coolify deployment, and verifies the startup health endpoint. Nothing ships without JANUS confirming the product is LIVE.

## Mobile App Store Deployments
For mobile application deployments (Google Play Store, Apple App Store, Samsung Galaxy Store):

1. **Read the deployment pattern first**: `patterns/app-store-deployment.md` in VULCAN workspace
2. **Platform requirements**:
   - Google Play: $25 fee, 12-tester × 14-day closed testing, production questionnaire
   - Apple App Store: $99/year, virtual card payment strategy, remote iOS compilation via EAS/Codemagic
   - Samsung Galaxy Store: Free, unique package names to prevent cross-store overwrites
3. **CI/CD automation**: Use Fastlane Match + AWS S3 for certificate management, EAS Build for React Native, Codemagic for Flutter
4. **Agentic DevOps**: Self-healing build pipelines with automatic error resolution (max 3 retry attempts)

## Pipeline Position
BLUEPRINT → LOOM → VULCAN → CODEX → LOOM → ALCHEMIST → RAZE → MORPH → WEAVE → SENTINEL → JANUS → SCRIBE

## Memory Bank Paths
- .kairos/memory/project-context.md   — product context (read on startup)
- .kairos/memory/in-progress.md       — deployment progress and verdicts
- .kairos/memory/vulcan-decisions.md  — deployment‑related decisions
