# Give Junie (JetBrains) memory that learns from your corrections

vidbyte-memory turns each correction you give Junie (JetBrains) into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

`/extensions marketplace add cerredz/vidbyte-memory`, or run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `.junie/AGENTS.md`, then `AGENTS.md`
- **Skills:** `.agents/skills/`, `.junie/skills/`

## Enforcement: Enforceable, wired by hand

Junie ignores project hooks by default; a Stop hook works inside a Junie extension's `hooks/hooks.json`.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://junie.jetbrains.com/docs

[All agents](README.md)
