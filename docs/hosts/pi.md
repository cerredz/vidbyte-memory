# Give Pi memory that learns from your corrections

vidbyte-memory turns each correction you give Pi into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md` or `CLAUDE.md`
- **Skills:** `.agents/skills/`, `.pi/skills/`

## Enforcement: Advisory

Pi has no built-in subagents or stop hook; an extension using `agent_before_settle` is planned.

Without a blocking hook, the checklist in `AGENTS.md` is the contract, kept by the agent.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://github.com/earendil-works/pi

[All agents](README.md)
