# Give Devin (CLI, cloud, Desktop) memory that learns from your corrections

vidbyte-memory turns each correction you give Devin (CLI, cloud, Desktop) into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

`devin plugins install cerredz/vidbyte-memory`, then run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md` (cloud Devin injects the first 16 KiB; this one is about 15 KiB)
- **Skills:** `.claude/skills/`, `.agents/skills/`, `.devin/skills/`

## Enforcement: Enforced in some products

Devin CLI reads `.claude/settings.json`, so the Stop hook applies. Devin Desktop (formerly Windsurf) has no blocking stop hook: advisory there.

## Notes

- Devin Desktop rules live in `.devin/rules/` (legacy `.windsurf/rules/`).

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://docs.devin.ai

[All agents](README.md)
