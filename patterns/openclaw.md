# OpenClaw Pattern — OVERLORD Empire Standard

## Config Location
```
/home/overlord/.openclaw/openclaw.json
```

## Agent Workspace Structure
```
/home/overlord/.openclaw/workspace/{AGENT_NAME}/
├── SOUL.md        ← behavioral spec (primary system prompt)
├── IDENTITY.md    ← role card
├── PERSONA.md     ← Victory's voice (shared across all agents)
├── TOOLS.md       ← infrastructure manifest
├── AGENTS.md      ← workspace rules + agent-specific red lines
├── MEMORY.md      ← long-term memory
├── DREAMS.md      ← aspirational context
├── HEARTBEAT.md   ← proactive task checklist
├── USER.md        ← Victory's profile
└── memory/
    └── YYYY-MM-DD.md  ← daily session logs
```

## Adding Agent to openclaw.json
```python
import json

with open('/home/overlord/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

new_agent = {
    "id": "agent_name_lowercase",
    "model": {
        "primary": "nim/meta/llama-3.3-70b-instruct"
    },
    "workspace": "/home/overlord/.openclaw/workspace/AGENT_NAME"
}

# Check for duplicates before appending
existing_ids = [a.get('id') for a in config['agents']['list']]
if new_agent['id'] not in existing_ids:
    config['agents']['list'].append(new_agent)

with open('/home/overlord/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)
```

## Model Tier Assignment
```
Fast agents (HOOK, HANDLER):     nim/meta/llama-3.1-8b-instruct
Large agents (RETAINER, HERMES): nim/meta/llama-3.3-70b-instruct
Smart agents (SPECTRAL, ORACLE): nim/nvidia/nemotron-3-super-120b-a12b
Deep agents (CLOSER, ARCHITECT): nim/deepseek-ai/deepseek-r1
Coder agents (VULCAN):           nim/minimaxai/minimax-m2.7
```

## SOUL.md Required Sections
```
# AGENT_NAME — SOUL FILE
## IDENTITY
## THE HUMANIZER
## [AGENT-SPECIFIC COVENANT / RULES]
## [AGENT] NEVER
## [AGENT] ALWAYS
## [AGENT] ROUTING LOGIC
## HARD OVERRIDES — FINAL AUTHORITY
## MEMORY RULES
```

## NEVER
- Never modify openclaw.json without explicit instruction from Your Majesty
- Never edit another agent's SOUL.md or MEMORY.md
- Never add an agent without checking for existing ID conflicts
- Never use system python — always /opt/overlord/venv/bin/python3 for scripts