# Give Hermes Agent memory that learns from your corrections

vidbyte-memory turns each correction you give Hermes Agent into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Run the installer, then `hermes skills trust` so Hermes loads project skills.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `.hermes.md`, then `AGENTS.md`, then `CLAUDE.md`
- **Skills:** `.agents/skills/` after `hermes skills trust`

## Enforcement: Enforceable, wired by hand

Add a `pre_verify` hook in Hermes's `config.yaml` running `python scripts/guard.py`; it accepts the Claude Code output. It fires on turns that edited code.

## Notes

- A Hermes plugin-catalog entry is planned.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://github.com/NousResearch/hermes-agent

[All agents](README.md)
