# Give Goose memory that learns from your corrections

vidbyte-memory turns each correction you give Goose into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

`goose plugin install https://github.com/cerredz/vidbyte-memory`, or run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md`, `.goosehints`
- **Skills:** `.agents/skills/`, `.claude/skills/`

## Enforcement: Enforceable, wired by hand

Goose supports a blocking Stop hook, capped by `GOOSE_STOP_HOOK_BLOCK_CAP`; point it at `python scripts/guard.py`.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://github.com/aaif-goose/goose

[All agents](README.md)
