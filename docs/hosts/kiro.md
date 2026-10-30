# Give Kiro memory that learns from your corrections

vidbyte-memory turns each correction you give Kiro into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Run the installer with `--agents kiro`, which also mirrors the skills into `.kiro/skills/`.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `.kiro/steering/*.md`, `AGENTS.md`
- **Skills:** `.kiro/skills/`

## Enforcement: Advisory

Kiro has a Stop trigger, but blocking is not documented.

Without a blocking hook, the checklist in `AGENTS.md` is the contract, kept by the agent.

## Notes

- A Kiro Powers listing is planned.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://kiro.dev/docs

[All agents](README.md)
