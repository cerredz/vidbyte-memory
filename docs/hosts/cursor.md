# Give Cursor memory that learns from your corrections

vidbyte-memory turns each correction you give Cursor into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md`; rules in `.cursor/rules/*.mdc`
- **Skills:** `.agents/skills/` (also `.claude/skills/`)

## Enforcement: Enforced

Cursor loads `.claude/settings.json` hooks by default and maps a Stop block to a follow-up message, so the Claude Code hook applies.

## Notes

- Subagents are read from `.cursor/agents/` and `.claude/agents/`.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://cursor.com/docs/hooks

[All agents](README.md)
