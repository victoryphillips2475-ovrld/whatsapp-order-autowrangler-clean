# BLUEPRINT — VULCAN Reference

## What BLUEPRINT Sends You
A complete BUILD PLAN containing:
- Stack (already decided — do not re-decide without flagging a hard conflict)
- File structure (every file to create)
- API schema (every endpoint)
- Database schema (every table)
- Environment variables (every var)
- MVP feature list (build only this — Post-Ship does not exist yet)
- Agent roster (who else is active on this build)

## What VULCAN Does When a BUILD PLAN Arrives
1. Read the full BUILD PLAN before touching any file
2. Read all pattern files for the selected stack
3. Create `.env.example` first — always
4. Build MVP features only
5. Create `Product.md` skeleton — SCRIBE fills it out
6. Create `design.md` skeleton if frontend exists — LOOM fills it out
7. Hand off to ALCHEMIST when build session ends

## Hard Rules
- Stack is BLUEPRINT's decision — flag conflicts, do not silently change
- MVP scope is locked — no features outside the BUILD PLAN MVP list
- `.env.example` is mandatory — no exceptions
- If a BUILD PLAN assumption blocks implementation, resolve it using available context — do not stop the pipeline
