# Give Amp memory that learns from your corrections

vidbyte-memory turns each correction you give Amp into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md` (falls back to `CLAUDE.md`)
- **Skills:** `.agents/skills/`, `.claude/skills/`

## Enforcement: Advisory

An Amp plugin can continue on `agent.end`; planned.

Without a blocking hook, the checklist in `AGENTS.md` is the contract, kept by the agent.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://ampcode.com/docs

[All agents](README.md)
