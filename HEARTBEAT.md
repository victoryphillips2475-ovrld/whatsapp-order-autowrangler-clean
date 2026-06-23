# VULCAN — HEARTBEAT

## Active Checks (rotate 1-2x per day)
- [ ] Any pending code tasks from OVERLORD?
- [ ] Any broken builds in /home/overlord/ that need fixing?
- [ ] Check VPS disk space: df -h /home/overlord
- [ ] Check Python venv integrity: /opt/overlord/venv/bin/python3 --version

## Proactive Work (heartbeat downtime)
- Review memory/YYYY-MM-DD.md files and update MEMORY.md
- Run git status on active KAIROS pipeline repos
- Check for dependency updates on active projects
- [ ] Verify handoff files in /home/overlord/.openclaw/shared/ follow naming convention

## When to reach out
- Build is broken and Victory hasn't noticed
- Critical dependency deprecated
- Disk space <10% on VPS
