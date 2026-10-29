# Give Qwen Code memory that learns from your corrections

vidbyte-memory turns each correction you give Qwen Code into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

`qwen extensions install cerredz/vidbyte-memory`, or run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `QWEN.md`, `AGENTS.md`
- **Skills:** `.agents/skills/`, `.qwen/skills/`

## Enforcement: Enforceable, wired by hand

Add a Stop hook to the project `settings.json` running `python scripts/guard.py`.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://github.com/QwenLM/qwen-code

[All agents](README.md)
