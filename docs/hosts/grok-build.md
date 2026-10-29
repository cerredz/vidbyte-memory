# Give Grok Build memory that learns from your corrections

vidbyte-memory turns each correction you give Grok Build into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Add `cerredz/vidbyte-memory` as a plugin marketplace, or run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md`, `CLAUDE.md`
- **Skills:** `.agents/skills/`, `.claude/skills/`

## Enforcement: Enforced

Grok Build reads `.claude/settings.json` hooks after you run `/hooks-trust`.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://github.com/xai-org/plugin-marketplace

[All agents](README.md)
