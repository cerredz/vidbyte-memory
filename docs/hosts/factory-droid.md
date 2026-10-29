# Give Factory Droid memory that learns from your corrections

vidbyte-memory turns each correction you give Factory Droid into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

`droid plugin marketplace add cerredz/vidbyte-memory`, then install the plugin. Or run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md`
- **Skills:** `.agents/skills/`, `.factory/skills/`

## Enforcement: Enforceable, wired by hand

Add a Stop hook to `.factory/hooks.json` running `python scripts/guard.py`; it uses the `decision: block` format.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://docs.factory.ai/cli/configuration/plugins

[All agents](README.md)
