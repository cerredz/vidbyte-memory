# Give Cline memory that learns from your corrections

vidbyte-memory turns each correction you give Cline into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md`, `.clinerules/`
- **Skills:** `.claude/skills/` (Cline does not read `.agents/skills/`)

## Enforcement: Advisory

A Cline plugin can queue a follow-up with `afterRun`; planned.

Without a blocking hook, the checklist in `AGENTS.md` is the contract, kept by the agent.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://docs.cline.bot

[All agents](README.md)
