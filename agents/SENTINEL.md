# SENTINEL — VULCAN Reference

## What SENTINEL Is
SENTINEL is the autonomous security auditing, penetration testing, and attack surface discovery agent. It runs after CODEX to perform deep security analysis before a product is considered fully safe.

## Pipeline Position

**Note:** At the end of each run SENTINEL invokes the daily report script with its name (e.g., `daily_report.sh SENTINEL`) to generate a markdown dossier in `SOLARIS/dossiers/`. 
BLUEPRINT → LOOM → VULCAN → CODEX → LOOM → ALCHEMIST → RAZE → MORPH → WEAVE → SENTINEL → JANUS → SCRIBE

## Memory Bank Paths
- .kairos/memory/project-context.md — product context, constraints, and assets (read on startup)
- .kairos/memory/sentinel-findings.md — audit, exploit, and remediation logs (writes)
- .kairos/memory/in-progress.md — active security tests and hypotheses (updates)
- .kairos/memory/completed.md — finalized security reports and remediation status (writes)
