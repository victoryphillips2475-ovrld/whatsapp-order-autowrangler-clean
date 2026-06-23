# ALCHEMIST — VULCAN Reference
See Kilo config for full prompt. This file is a pipeline position reference.

ALCHEMIST: Pre-build gate. Runs after BLUEPRINT confirms BUILD PLAN, before VULCAN writes code.
RAZE:      Post-build critic. Runs after VULCAN signals build complete.
MORPH:     Post-RAZE cleanup. Runs when RAZE issues MEDIUM/BLOAT findings.

PIPELINE POSITION:
BLUEPRINT → LOOM → VULCAN → CODEX → LOOM → ALCHEMIST → RAZE → MORPH → WEAVE → SENTINEL → JANUS → SCRIBE

MEMORY BANK PATHS:
  .kairos/memory/project-context.md   — product context (read on startup)
  .kairos/memory/vulcan-decisions.md  — architecture decisions (read on startup)
  .kairos/memory/alchemist-log.md     — audit history (ALCHEMIST writes, RAZE reads)
  .kairos/memory/raze-findings.md     — critique history (RAZE writes, MORPH reads)
  .kairos/memory/in-progress.md       — active tasks (all agents update)
