# Give GitHub Copilot (CLI, VS Code, cloud agent) memory that learns from your corrections

vidbyte-memory turns each correction you give GitHub Copilot (CLI, VS Code, cloud agent) into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Run the installer. A listing in awesome-copilot, Copilot's default marketplace, is pending.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`
- **Skills:** `.github/skills/`, `.claude/skills/`, `.agents/skills/`

## Enforcement: Enforced

The installer writes `.github/hooks/vidbyte-memory.json` with an `agentStop` hook (bash and PowerShell). The CLI gives up after 8 blocks in a row; the guard stops after 5.

## Notes

- In the cloud agent only the bash command runs, and the platform pushes for you, so the guard's push check may need to be relaxed there.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://docs.github.com/en/copilot/reference/hooks-configuration

[All agents](README.md)
