# Give Warp memory that learns from your corrections

vidbyte-memory turns each correction you give Warp into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md` (`WARP.md` wins when both exist)
- **Skills:** `.agents/skills/`

## Enforcement: Advisory

Warp has no stop hook.

Without a blocking hook, the checklist in `AGENTS.md` is the contract, kept by the agent.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://docs.warp.dev

[All agents](README.md)
